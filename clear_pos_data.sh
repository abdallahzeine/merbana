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

[[ -f "${DB}" ]] || fail "Database not found: ${DB}"

# ── Show current row counts ────────────────────────────────────────────────────
show_counts() {
  sqlite3 "${DB}" <<'SQL'
.mode column
.headers on
SELECT 'orders'            AS "table", COUNT(*) AS rows FROM orders
UNION ALL
SELECT 'order_items',                  COUNT(*)        FROM order_items
UNION ALL
SELECT 'cash_transactions',            COUNT(*)        FROM cash_transactions
UNION ALL
SELECT 'debtors',                      COUNT(*)        FROM debtors;
SQL
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
sqlite3 "${DB}" <<'SQL'
PRAGMA foreign_keys = ON;
BEGIN;
DELETE FROM order_items;
DELETE FROM cash_transactions;
DELETE FROM orders;
DELETE FROM debtors;
COMMIT;
SQL

ok "Tables cleared."

# ── Verify ────────────────────────────────────────────────────────────────────
echo
info "Row counts after clear:"
show_counts
