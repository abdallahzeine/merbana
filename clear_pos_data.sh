#!/usr/bin/env bash
set -euo pipefail

# clear_pos_data.sh — Wipes orders, cash transactions, and debtors from the POS database.
# Products, categories, users, and settings are left untouched.
#
# Usage: bash clear_pos_data.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

info() { echo -e "${CYAN}[INFO] $*${RESET}"; }
ok()   { echo -e "${GREEN}[OK] $*${RESET}"; }
warn() { echo -e "${YELLOW}[WARN] $*${RESET}"; }
fail() { echo -e "${RED}[ERROR] $*${RESET}" >&2; exit 1; }

POS_DIR="${POS_DIR:-$HOME/Desktop/POS}"
DB="${POS_DIR}/data/merbana.db"
BACKUP_DIR="${POS_DIR}/backups"
PYTHON="${POS_DIR}/.venv/bin/python"

[[ -f "${DB}" ]] || fail "Database not found: ${DB}"
[[ -x "${PYTHON}" ]] || fail "Python venv not found: ${PYTHON}"

# ── Show current row counts ────────────────────────────────────────────────────
show_counts() {
  "${PYTHON}" - "${DB}" <<'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])
tables = ["orders", "order_items", "cash_transactions", "debtors"]
print(f"  {'table':<25} {'rows':>6}")
print(f"  {'-'*25} {'-'*6}")
for t in tables:
    n = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:<25} {n:>6}")
db.close()
PY
}

echo
info "Current row counts:"
show_counts

# ── Confirm ────────────────────────────────────────────────────────────────────
echo
warn "This will permanently delete all orders, order items, cash transactions, and debtors."
warn "Products, categories, users, and settings will NOT be affected."
echo -n "Type YES to continue: "
read -r confirm
[[ "${confirm}" == "YES" ]] || { info "Aborted."; exit 0; }

# ── Backup ─────────────────────────────────────────────────────────────────────
mkdir -p "${BACKUP_DIR}"
ts="$(date +%Y%m%d_%H%M%S)"
backup_path="${BACKUP_DIR}/merbana_before_clear_${ts}.db"
cp "${DB}" "${backup_path}"
ok "Backup saved: ${backup_path}"

# ── Clear tables ──────────────────────────────────────────────────────────────
info "Clearing tables..."
"${PYTHON}" - "${DB}" <<'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])
db.execute("PRAGMA foreign_keys = ON")
db.execute("DELETE FROM order_items")
db.execute("DELETE FROM cash_transactions")
db.execute("DELETE FROM orders")
db.execute("DELETE FROM debtors")
db.commit()
db.close()
PY

ok "Tables cleared."

# ── Verify ────────────────────────────────────────────────────────────────────
echo
info "Row counts after clear:"
show_counts
