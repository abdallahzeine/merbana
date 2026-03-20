#!/usr/bin/env bash
set -euo pipefail

# One-command Linux setup for Merbana POS on a target machine.
# What it does:
# 1) Installs Ubuntu dependencies (Python, Node, GTK/WebKit for pywebview)
# 2) Builds frontend (npm ci + npm run build)
# 3) Creates Desktop POS layout (~/Desktop/POS by default)
# 4) Creates app venv and installs pywebview with distro-aware pinning
# 5) Writes launcher wrapper script
# 6) Creates desktop shortcut (.desktop)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

info() { echo -e "${CYAN}[INFO] $*${RESET}"; }
ok() { echo -e "${GREEN}[OK] $*${RESET}"; }
warn() { echo -e "${YELLOW}[WARN] $*${RESET}"; }
fail() { echo -e "${RED}[ERROR] $*${RESET}" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
POS_DIR="${POS_DIR:-${HOME}/Desktop/POS}"
VENV_DIR="${VENV_DIR:-${POS_DIR}/.venv}"
WRAPPER_PATH="${WRAPPER_PATH:-${POS_DIR}/Merbana}"
DESKTOP_FILE="${DESKTOP_FILE:-${HOME}/Desktop/Merbana.desktop}"
APP_MENU_FILE="${HOME}/.local/share/applications/Merbana.desktop"
LAUNCHER_PY="${REPO_DIR}/Deployment/merbana_launcher.py"
DIST_SRC="${REPO_DIR}/dist"
DIST_DST="${POS_DIR}/dist"
DATA_DIR="${POS_DIR}/data"
ARTIFACTS_DIR="${POS_DIR}/artifacts"
BACKUPS_DIR="${POS_DIR}/backups"

WEBKIT_GIR_PACKAGE=""
PYWEBVIEW_SPEC="${PYWEBVIEW_SPEC:-}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1"
}

require_sudo() {
  require_cmd sudo
  if ! sudo -n true >/dev/null 2>&1; then
    info "Sudo access is required for OS package installation."
    sudo -v
  fi
}

parse_ubuntu_release() {
  if [[ ! -f /etc/os-release ]]; then
    fail "Cannot detect distribution: /etc/os-release not found"
  fi

  # shellcheck disable=SC1091
  source /etc/os-release
  DISTRO_ID="${ID:-unknown}"
  DISTRO_VERSION="${VERSION_ID:-0}"

  if [[ "${DISTRO_ID}" != "ubuntu" ]]; then
    fail "Unsupported distribution: ${DISTRO_ID}. This installer supports Ubuntu only."
  fi

  info "Detected Ubuntu version: ${DISTRO_VERSION}"
}

choose_webkit_package() {
  case "${DISTRO_VERSION}" in
    24.*|25.*|26.*) WEBKIT_GIR_PACKAGE="gir1.2-webkitgtk-6.0" ;;
    22.*|23.*)       WEBKIT_GIR_PACKAGE="gir1.2-webkit2-4.1" ;;
    20.*|21.*)       WEBKIT_GIR_PACKAGE="gir1.2-webkit2-4.0" ;;
    *)               WEBKIT_GIR_PACKAGE="gir1.2-webkit2-4.1" ;;
  esac

  if [[ -z "${PYWEBVIEW_SPEC}" ]]; then
    case "${WEBKIT_GIR_PACKAGE}" in
      gir1.2-webkitgtk-6.0) PYWEBVIEW_SPEC="pywebview>=5,<6" ;;
      gir1.2-webkit2-4.1)   PYWEBVIEW_SPEC="pywebview>=4.4,<5" ;;
      gir1.2-webkit2-4.0)   PYWEBVIEW_SPEC="pywebview>=3.7,<4" ;;
      *)                    PYWEBVIEW_SPEC="pywebview>=4,<6" ;;
    esac
  fi

  info "Using GTK WebKit package: ${WEBKIT_GIR_PACKAGE}"
  info "Using pywebview spec: ${PYWEBVIEW_SPEC}"
}

install_os_dependencies() {
  if ! command -v apt-get >/dev/null 2>&1; then
    fail "apt-get not found. This installer supports Ubuntu only."
  fi

  require_sudo
  sudo apt-get update

  local base_packages=(
    git
    curl
    python3
    python3-venv
    python3-pip
    python3-gi
    python3-gi-cairo
    gir1.2-gtk-3.0
    nodejs
    npm
  )

  local webkit_package="${WEBKIT_GIR_PACKAGE}"
  local webkit_fallbacks=("gir1.2-webkitgtk-6.0" "gir1.2-webkit2-4.1" "gir1.2-webkit2-4.0")

  info "Installing base OS packages via apt"
  sudo apt-get install -y "${base_packages[@]}"

  info "Installing WebKit GTK package (${webkit_package})"
  if ! sudo apt-get install -y "${webkit_package}"; then
    warn "Primary WebKit package install failed, trying compatible fallbacks"
    local installed=false
    local candidate
    for candidate in "${webkit_fallbacks[@]}"; do
      if sudo apt-get install -y "${candidate}"; then
        WEBKIT_GIR_PACKAGE="${candidate}"
        installed=true
        break
      fi
    done
    if [[ "${installed}" != true ]]; then
      fail "Could not install any supported WebKit GTK package"
    fi
  fi
}

build_frontend() {
  [[ -f "${REPO_DIR}/package.json" ]] || fail "package.json not found at ${REPO_DIR}"

  info "Installing Node dependencies"
  (cd "${REPO_DIR}" && npm ci)

  info "Building frontend"
  (cd "${REPO_DIR}" && npm run build)

  [[ -f "${DIST_SRC}/index.html" ]] || fail "Build output missing: ${DIST_SRC}/index.html"
  ok "Frontend build complete"
}

setup_pos_layout() {
  info "Creating POS layout at ${POS_DIR}"
  mkdir -p "${POS_DIR}" "${DATA_DIR}" "${ARTIFACTS_DIR}" "${BACKUPS_DIR}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "${DIST_SRC}/" "${DIST_DST}/"
  else
    rm -rf "${DIST_DST}"
    cp -r "${DIST_SRC}" "${DIST_DST}"
  fi

  ok "POS layout ready"
}

setup_venv_and_python_deps() {
  info "Creating Python virtual environment at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"

  info "Installing Python dependencies in venv"
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
  "${VENV_DIR}/bin/pip" install "${PYWEBVIEW_SPEC}"

  ok "Python environment ready"
}

write_wrapper() {
  info "Writing launcher wrapper at ${WRAPPER_PATH}"

  cat > "${WRAPPER_PATH}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

POS_DIR="${POS_DIR}"
VENV_PY="${VENV_DIR}/bin/python"
LAUNCHER_PY="${LAUNCHER_PY}"

export MERBANA_DIST_PATH="${DIST_DST}"
export MERBANA_DATA_PATH="${DATA_DIR}"

mkdir -p "${DATA_DIR}"

if [[ ! -x "\${VENV_PY}" ]]; then
  echo "[ERROR] Python venv not found at \${VENV_PY}" >&2
  exit 1
fi

if [[ ! -f "\${LAUNCHER_PY}" ]]; then
  echo "[ERROR] Launcher not found at \${LAUNCHER_PY}" >&2
  exit 1
fi

exec "\${VENV_PY}" "\${LAUNCHER_PY}"
EOF

  chmod +x "${WRAPPER_PATH}"
  ok "Wrapper created"
}

write_desktop_shortcut() {
  info "Creating desktop shortcut at ${DESKTOP_FILE}"
  mkdir -p "$(dirname "${DESKTOP_FILE}")" "$(dirname "${APP_MENU_FILE}")"

  cat > "${DESKTOP_FILE}" <<EOF
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

  chmod +x "${DESKTOP_FILE}"
  cp "${DESKTOP_FILE}" "${APP_MENU_FILE}"

  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$(dirname "${APP_MENU_FILE}")" >/dev/null 2>&1 || true
  fi

  ok "Desktop shortcut created"
}

print_summary() {
  echo
  ok "Merbana Linux target setup completed"
  echo "  Repo:        ${REPO_DIR}"
  echo "  POS dir:     ${POS_DIR}"
  echo "  Venv:        ${VENV_DIR}"
  echo "  Wrapper:     ${WRAPPER_PATH}"
  echo "  Shortcut:    ${DESKTOP_FILE}"
  echo "  pywebview:   ${PYWEBVIEW_SPEC}"
  echo
  echo "Run the app with: ${WRAPPER_PATH}"
}

main() {
  parse_ubuntu_release
  choose_webkit_package
  install_os_dependencies
  build_frontend
  setup_pos_layout
  setup_venv_and_python_deps
  write_wrapper
  write_desktop_shortcut
  print_summary
}

main "$@"
