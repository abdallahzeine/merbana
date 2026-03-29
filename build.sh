#!/usr/bin/env bash
set -euo pipefail

# build.sh — One-command build + install for Merbana POS on Lubuntu 20.04
# Usage: bash build.sh
#
# Optional: place data.json next to this script to auto-migrate legacy data.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

info() { echo -e "${CYAN}[INFO] $*${RESET}"; }
ok()   { echo -e "${GREEN}[OK] $*${RESET}"; }
warn() { echo -e "${YELLOW}[WARN] $*${RESET}"; }
fail() { echo -e "${RED}[ERROR] $*${RESET}" >&2; exit 1; }

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POS_DIR="${POS_DIR:-${HOME}/Desktop/POS}"
VENV_DIR="${POS_DIR}/.venv"
POS_APP_DIR="${POS_DIR}/app"
BACKEND_DST_DIR="${POS_APP_DIR}/backend"
DEPLOY_BACKEND_DST_DIR="${POS_APP_DIR}/Deployment/backend"
DIST_DST="${POS_DIR}/dist"
DATA_DIR="${POS_DIR}/data"
ARTIFACTS_DIR="${POS_DIR}/artifacts"
BACKUPS_DIR="${POS_DIR}/backups"
ALEMBIC_INI_DST="${DEPLOY_BACKEND_DST_DIR}/alembic.ini"
RUNTIME_LAUNCHER_PY="${POS_DIR}/merbana_pos_launcher.py"
WRAPPER_PATH="${POS_DIR}/Merbana"
DESKTOP_FILE="${HOME}/Desktop/Merbana.desktop"
APP_MENU_FILE="${HOME}/.local/share/applications/Merbana.desktop"
POS_DESKTOP_FILE="${POS_DIR}/Merbana.desktop"
MIGRATION_SCRIPT_DST="${POS_DIR}/migrate_json_to_sqlite.py"

# ── Constants (Ubuntu 20.04 Focal) ─────────────────────────────────────────────
PYTHON_VERSION="${PYTHON_VERSION:-3.12.10}"
NODE_MAJOR="20"
UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1"
}

require_sudo() {
  require_cmd sudo
  if ! sudo -n true >/dev/null 2>&1; then
    info "Sudo access required for package installation."
    sudo -v
  fi
}

# ── Step 1: Verify OS ──────────────────────────────────────────────────────────
verify_os() {
  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "${ID:-}" != "ubuntu" ]]; then
      warn "This script targets Ubuntu 20.04. Detected: ${ID:-unknown}. Continuing anyway."
    elif [[ "${VERSION_ID:-}" != "20.04" ]]; then
      warn "This script targets Ubuntu 20.04. Detected: ${VERSION_ID:-unknown}. Continuing anyway."
    else
      info "Detected Ubuntu ${VERSION_ID} — OK"
    fi
  else
    warn "/etc/os-release not found. Cannot verify OS. Continuing."
  fi
}

# ── Step 2: Install OS packages ────────────────────────────────────────────────
install_os_packages() {
  require_sudo
  sudo apt-get update -qq

  info "Installing OS packages"
  sudo apt-get install -y \
    git curl \
    python3 python3-venv python3-pip \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-webkit2-4.0

  ok "OS packages installed"
}

# ── Step 3: Install Node.js 20 LTS ────────────────────────────────────────────
install_nodejs() {
  if command -v node >/dev/null 2>&1; then
    local current_major
    current_major="$(node -e 'process.stdout.write(process.version.split(".")[0].slice(1))')"
    if (( current_major >= NODE_MAJOR )); then
      ok "Node.js $(node --version) already installed"
      return
    fi
    warn "Node.js $(node --version) found but Vite 7 requires >= ${NODE_MAJOR}.19.0 — upgrading"
  fi

  info "Installing Node.js ${NODE_MAJOR} LTS via NodeSource"
  require_cmd curl
  curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | sudo bash -
  sudo apt-get install -y nodejs
  ok "Node.js $(node --version) installed"
}

# ── Step 4: Install uv + Python ───────────────────────────────────────────────
ensure_uv_and_python() {
  if [[ ! -x "${UV_BIN}" ]]; then
    info "Installing uv"
    require_cmd curl
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
  [[ -x "${UV_BIN}" ]] || fail "uv not found at ${UV_BIN}"

  info "Installing Python ${PYTHON_VERSION}"
  "${UV_BIN}" python install "${PYTHON_VERSION}"
  ok "Python ${PYTHON_VERSION} ready"
}

# ── Step 5: Build frontend ─────────────────────────────────────────────────────
build_frontend() {
  [[ -f "${REPO_DIR}/package.json" ]] || fail "package.json not found at ${REPO_DIR}"
  require_cmd npm

  info "Installing Node dependencies"
  (cd "${REPO_DIR}" && npm ci)

  info "Building React frontend"
  (cd "${REPO_DIR}" && npm run build)

  [[ -f "${REPO_DIR}/dist/index.html" ]] || fail "Build failed: dist/index.html not found"
  ok "Frontend build complete"
}

# ── Step 6: Create POS layout ─────────────────────────────────────────────────
setup_pos_layout() {
  info "Creating POS layout at ${POS_DIR}"
  mkdir -p "${POS_DIR}" "${DATA_DIR}" "${ARTIFACTS_DIR}" "${BACKUPS_DIR}" "${POS_APP_DIR}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "${REPO_DIR}/dist/" "${DIST_DST}/"
  else
    rm -rf "${DIST_DST}"
    cp -r "${REPO_DIR}/dist" "${DIST_DST}"
  fi

  ok "POS layout ready"
}

# ── Step 7: Copy backend sources ──────────────────────────────────────────────
copy_runtime_sources() {
  [[ -d "${REPO_DIR}/backend" ]]             || fail "Backend source missing: ${REPO_DIR}/backend"
  [[ -d "${REPO_DIR}/Deployment/backend" ]] || fail "Alembic source missing: ${REPO_DIR}/Deployment/backend"

  info "Copying backend sources"
  mkdir -p "${BACKEND_DST_DIR}" "${POS_APP_DIR}/Deployment" "${DEPLOY_BACKEND_DST_DIR}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "${REPO_DIR}/backend/"            "${BACKEND_DST_DIR}/"
    rsync -a --delete "${REPO_DIR}/Deployment/backend/" "${DEPLOY_BACKEND_DST_DIR}/"
  else
    rm -rf "${BACKEND_DST_DIR}" "${DEPLOY_BACKEND_DST_DIR}"
    mkdir -p "${BACKEND_DST_DIR}" "${DEPLOY_BACKEND_DST_DIR}"
    cp -r "${REPO_DIR}/backend/."            "${BACKEND_DST_DIR}/"
    cp -r "${REPO_DIR}/Deployment/backend/." "${DEPLOY_BACKEND_DST_DIR}/"
  fi

  ok "Backend sources copied"
}

# ── Step 8: Create venv + install deps ────────────────────────────────────────
setup_venv_and_python_deps() {
  info "Creating Python ${PYTHON_VERSION} venv at ${VENV_DIR}"
  "${UV_BIN}" venv --python "${PYTHON_VERSION}" --seed "${VENV_DIR}"

  [[ -x "${VENV_DIR}/bin/python" ]] || fail "Python not found in venv: ${VENV_DIR}/bin/python"

  info "Installing Python dependencies"
  "${UV_BIN}" pip install --python "${VENV_DIR}/bin/python" --upgrade pip setuptools wheel
  "${UV_BIN}" pip install --python "${VENV_DIR}/bin/python" -r "${REPO_DIR}/requirements.txt"
  "${UV_BIN}" pip install --python "${VENV_DIR}/bin/python" "uvicorn[standard]" "pydantic-settings"
  # Note: pywebview is not installed — runtime is browser-based (uvicorn + xdg-open).
  # pywebview 3.x is incompatible with Python 3.12; 5.x requires WebKit 6.0 (Ubuntu 24+ only).

  ok "Python environment ready"
}

# ── Step 9: Run Alembic migrations ────────────────────────────────────────────
run_migrations() {
  [[ -f "${ALEMBIC_INI_DST}" ]] || fail "Alembic config not found: ${ALEMBIC_INI_DST}"

  local db_url="sqlite:///${DATA_DIR}/merbana.db"

  info "Running Alembic migrations"
  MERBANA_DIST_PATH="${DIST_DST}" \
  MERBANA_DATA_PATH="${DATA_DIR}" \
  MERBANA_DB_URL="${db_url}" \
    "${VENV_DIR}/bin/python" -m alembic -c "${ALEMBIC_INI_DST}" upgrade head

  ok "Database migrations complete"
}

# ── Step 9b: Copy migration script ────────────────────────────────────────────
copy_migration_script() {
  local src="${REPO_DIR}/Deployment/migrate_json_to_sqlite.py"
  [[ -f "${src}" ]] || { warn "migrate_json_to_sqlite.py not found — skipping copy"; return; }

  cp "${src}" "${MIGRATION_SCRIPT_DST}"
  chmod +x "${MIGRATION_SCRIPT_DST}"
  ok "Migration script copied to ${MIGRATION_SCRIPT_DST}"
}

# ── Step 9c: Auto-migrate JSON if present ─────────────────────────────────────
auto_migrate_json() {
  local json_src="${REPO_DIR}/data.json"
  [[ -f "${json_src}" ]] || { info "No data.json found next to build.sh — skipping JSON migration"; return; }

  info "data.json detected — migrating legacy JSON to SQLite"
  local json_dst="${DATA_DIR}/data.json"
  cp "${json_src}" "${json_dst}"

  MERBANA_DATA_PATH="${DATA_DIR}" \
    "${VENV_DIR}/bin/python" "${MIGRATION_SCRIPT_DST}" \
      --source "${json_dst}" \
      --artifacts-dir "${ARTIFACTS_DIR}" \
      --overwrite

  ok "JSON migration complete"
}

# ── Step 10: Write runtime launcher ───────────────────────────────────────────
write_runtime_launcher() {
  info "Writing runtime launcher at ${RUNTIME_LAUNCHER_PY}"
  cat > "${RUNTIME_LAUNCHER_PY}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POS_DIR="${SCRIPT_DIR}"
VENV_DIR="${POS_DIR}/.venv"
APP_DIR="${POS_DIR}/app"
DATA_DIR="${POS_DIR}/data"
DIST_DIR="${POS_DIR}/dist"
LOG_FILE="${DATA_DIR}/launcher.log"
PID_FILE="${DATA_DIR}/merbana.pid"
HOST="127.0.0.1"
PORT="${MERBANA_PORT:-8741}"

VENV_PY="${VENV_DIR}/bin/python"

mkdir -p "${DATA_DIR}"

# If a PID file exists and the process is still alive, just open the browser.
if [[ -f "${PID_FILE}" ]]; then
  existing_pid="$(cat "${PID_FILE}")"
  if kill -0 "${existing_pid}" 2>/dev/null; then
    echo "Merbana already running (PID ${existing_pid}) — opening browser."
    xdg-open "http://${HOST}:${PORT}" || echo "Open http://${HOST}:${PORT} in your browser."
    exit 0
  else
    # Stale PID file — process is gone, clean up and start fresh.
    rm -f "${PID_FILE}"
  fi
fi

MERBANA_DIST_PATH="${DIST_DIR}" \
MERBANA_DATA_PATH="${DATA_DIR}" \
MERBANA_DB_URL="sqlite:///${DATA_DIR}/merbana.db" \
nohup "${VENV_PY}" -m uvicorn backend.app:app \
  --host "${HOST}" --port "${PORT}" \
  --app-dir "${APP_DIR}" > "${LOG_FILE}" 2>&1 &

echo $! > "${PID_FILE}"

timeout=30
until curl -s "http://${HOST}:${PORT}/api/health" | grep -q '"status":'; do
  timeout=$((timeout-1))
  if [ "${timeout}" -le 0 ]; then
    echo "Backend failed to start. Check ${LOG_FILE} for details."
    rm -f "${PID_FILE}"
    exit 1
  fi
  sleep 1
done

xdg-open "http://${HOST}:${PORT}" || echo "Open http://${HOST}:${PORT} in your browser."
EOF
  chmod +x "${RUNTIME_LAUNCHER_PY}"
  ok "Runtime launcher created"
}

# ── Step 11: Write wrapper ─────────────────────────────────────────────────────
write_wrapper() {
  info "Writing wrapper at ${WRAPPER_PATH}"
  cat > "${WRAPPER_PATH}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

VENV_PY="${VENV_DIR}/bin/python"
LAUNCHER="${RUNTIME_LAUNCHER_PY}"

[[ -x "\${VENV_PY}" ]] || { echo "[ERROR] venv not found at \${VENV_PY}" >&2; exit 1; }
[[ -f "\${LAUNCHER}" ]] || { echo "[ERROR] launcher not found at \${LAUNCHER}" >&2; exit 1; }

exec bash "\${LAUNCHER}"
EOF
  chmod +x "${WRAPPER_PATH}"
  ok "Wrapper created"
}

# ── Step 12: Create desktop shortcuts ─────────────────────────────────────────
write_desktop_shortcut() {
  info "Creating desktop shortcuts"
  mkdir -p "$(dirname "${DESKTOP_FILE}")" "$(dirname "${APP_MENU_FILE}")"

  cat > "${POS_DESKTOP_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Merbana POS
Comment=Launch Merbana POS
Exec=${WRAPPER_PATH}
Terminal=false
Categories=Office;
StartupNotify=true
Path=${POS_DIR}
EOF

  cp "${POS_DESKTOP_FILE}" "${DESKTOP_FILE}"
  cp "${POS_DESKTOP_FILE}" "${APP_MENU_FILE}"
  chmod +x "${POS_DESKTOP_FILE}" "${DESKTOP_FILE}" "${APP_MENU_FILE}"

  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$(dirname "${APP_MENU_FILE}")" >/dev/null 2>&1 || true
  fi

  ok "Desktop shortcuts created"
}

# ── Step 13: Summary ──────────────────────────────────────────────────────────
print_summary() {
  echo
  ok "Merbana POS installed successfully"
  echo "  POS dir   : ${POS_DIR}"
  echo "  Launcher  : ${WRAPPER_PATH}"
  echo "  Shortcut  : ${DESKTOP_FILE}"
  echo "  Database  : ${DATA_DIR}/merbana.db"
  echo
  echo "Double-click Merbana on the Desktop, or run:"
  echo "  ${WRAPPER_PATH}"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  verify_os
  install_os_packages
  install_nodejs
  ensure_uv_and_python
  build_frontend
  setup_pos_layout
  copy_runtime_sources
  setup_venv_and_python_deps
  run_migrations
  copy_migration_script
  auto_migrate_json
  write_runtime_launcher
  write_wrapper
  write_desktop_shortcut
  print_summary
}

main "$@"
