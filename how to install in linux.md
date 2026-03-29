# How to Install Merbana on Linux

## Overview

There are two ways to deploy Merbana on Linux:

| Method | Best for | Result |
|--------|----------|--------|
| **Script install** (`setup_linux_pos.sh`) | Target POS machine (Ubuntu) | `~/Desktop/POS/` layout with venv + desktop shortcut |
| **Binary build** (`build_linux.py`) | Developer building a distributable | Single `Merbana` binary via PyInstaller |

Both methods only support **Ubuntu** (20.04, 22.04, 24.04+). The script method is the standard way to deploy to a POS machine.

---

## Method 1: Script Install (Recommended for POS machines)

This is the standard production install. Run once on the target Ubuntu machine.

### Prerequisites

- Ubuntu 20.04 / 22.04 / 24.04+
- `sudo` access
- `git`, `curl`, `npm` available
- The repository cloned somewhere on the machine (e.g. `~/Desktop/merbana`)

### Run the setup script

```bash
cd ~/Desktop/merbana
bash Deployment/setup_linux_pos.sh
```

You can override defaults via environment variables:

```bash
REPO_DIR=~/Desktop/merbana \
POS_DIR=~/Desktop/POS \
PYTHON_VERSION=3.12.10 \
bash Deployment/setup_linux_pos.sh
```

### What the script does (step by step)

1. **Detects Ubuntu version** from `/etc/os-release` and selects the correct WebKit GTK package:
   - Ubuntu 24.x / 25.x / 26.x → `gir1.2-webkitgtk-6.0` + `pywebview>=5,<6`
   - Ubuntu 22.x / 23.x → `gir1.2-webkit2-4.1` + `pywebview>=4.4,<5`
   - Ubuntu 20.x / 21.x → `gir1.2-webkit2-4.0` + `pywebview>=3.7,<4`

2. **Installs OS packages** via `apt`:
   ```
   git curl python3 python3-venv python3-pip
   python3-gi python3-gi-cairo gir1.2-gtk-3.0
   <webkit-package-for-your-ubuntu-version>
   ```

3. **Installs `uv`** (Python package manager) from `astral.sh`, then installs **Python 3.12.10** via `uv`.

4. **Builds the React frontend**:
   ```bash
   cd ~/Desktop/merbana && npm ci && npm run build
   # Output: dist/index.html + assets
   ```

5. **Creates the POS directory layout**:
   ```
   ~/Desktop/POS/
     .venv/                  Python virtual environment
     app/
       backend/              FastAPI backend (copied from repo)
       Deployment/backend/   Alembic config + migration files
     dist/                   React SPA build output
     data/                   SQLite database + logs (created at runtime)
     artifacts/              Migration reports
     backups/                Update backups
     merbana_pos_launcher.py Runtime launcher (bash script)
     Merbana                 Executable wrapper
     Merbana.desktop         Desktop shortcut
   ```

6. **Creates a Python venv** using `uv` and installs:
   - All packages from `requirements.txt`
   - `pywebview` (version matched to WebKit)
   - `uvicorn[standard]`
   - `pydantic-settings`

7. **Runs Alembic migrations** to initialize the SQLite database:
   ```bash
   MERBANA_DB_URL="sqlite:////home/<user>/Desktop/POS/data/merbana.db" \
   python -m alembic -c ~/Desktop/POS/app/Deployment/backend/alembic.ini upgrade head
   ```

8. **Writes the runtime launcher** (`merbana_pos_launcher.py`) — a bash script that:
   - Starts FastAPI via `uvicorn backend.app:app` on `127.0.0.1:8741`
   - Waits for the health endpoint (`/api/health`)
   - Opens the browser via `xdg-open`

9. **Creates desktop shortcuts**:
   - `~/Desktop/Merbana.desktop`
   - `~/.local/share/applications/Merbana.desktop`
   - Both use `Terminal=false` (no console window)

### After install

Double-click **Merbana** on the desktop, or run:
```bash
~/Desktop/POS/Merbana
```

The app opens at `http://127.0.0.1:8741` in the system browser.

---

## Method 2: Binary Build (PyInstaller)

Use this to produce a single `Merbana` executable that can be copied to other machines.

> **Must be run on a Linux machine.** The binary is dynamically linked to system libs and is not portable across major OS versions.

### Prerequisites (build machine)

```bash
# GTK backend (default)
sudo apt install \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-webkit2-4.1 \
    libgtk-3-dev libwebkit2gtk-4.1-dev \
    nodejs npm

pip install pyinstaller pywebview

# OR Qt backend instead of GTK:
pip install PyQt5 PyQtWebEngine qtpy
```

### Build

```bash
# GTK backend (default)
python Deployment/build_linux.py

# Qt backend
python Deployment/build_linux.py --backend qt

# Skip frontend rebuild (reuse existing dist/)
python Deployment/build_linux.py --skip-frontend
```

### What the build does

1. Runs `npm run build` → produces `dist/` (React SPA)
2. Runs PyInstaller with `--onefile --noconsole`:
   - Embeds `dist/` inside the binary via `--add-data dist:dist`
   - Hidden imports for pywebview + GTK or Qt
3. Output: `dist_linux/Merbana` (single executable, ~chmod 755)
4. Cleans up PyInstaller work artifacts (`build_pyinstaller/`, `Merbana.spec`)

### Distributing the binary

Copy `dist_linux/Merbana` to the target machine. The target machine needs:

| Ubuntu version | Required package |
|----------------|-----------------|
| 24.04+ | `sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkitgtk-6.0` |
| 22.04 | `sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1` |
| 20.04 | `sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.0` |

Then run:
```bash
chmod +x Merbana
./Merbana
```

Data is stored at `<exe_dir>/data/merbana.db`. Run Alembic migrations before first launch:
```bash
MERBANA_DB_URL='sqlite:////absolute/path/to/data/merbana.db' \
python3 -m alembic -c Deployment/backend/alembic.ini upgrade head
```

---

## Runtime Architecture

When running (either method), the flow is:

```
merbana_launcher.py  (or uvicorn for script install)
  ├─ Starts FastAPI on http://127.0.0.1:8741
  ├─ Serves React SPA from dist/
  └─ Opens native window via pywebview
       └─ Falls back to: system browser + tkinter control window
```

- Port: `8741` (override with `MERBANA_PORT` env var; auto-increments up to 8840 if taken)
- Database: `data/merbana.db` (SQLite, WAL mode)
- Logs: `data/merbana.log`
- `data/` lives **outside** any PyInstaller bundle, beside the executable

---

## Updating an Existing Install (script method)

```bash
cd ~/Desktop/merbana
bash Deployment/update_merbana.sh
```

Override defaults:
```bash
REPO_DIR=~/Desktop/merbana \
BRANCH=main \
POS_DIR=~/Desktop/POS \
RETENTION=3 \
bash Deployment/update_merbana.sh
```

The update script:
1. Creates a timestamped backup of `dist/`, `merbana.db`, `merbana.db-wal`, `merbana.db-shm`
2. `git fetch` + `git reset --hard origin/main`
3. `npm ci && npm run build`
4. Deploys new `dist/` to POS dir, restores data files from backup
5. Stops running app processes (`pkill`)
6. Migrates legacy JSON → SQLite if needed (only if `merbana.db` doesn't exist yet, or `FORCE_JSON_REIMPORT=1`)
7. Runs `alembic upgrade head`
8. Restarts app via `nohup ./Merbana`
9. Polls `/api/health` for up to 35 seconds
10. Retains last 3 backups (configurable via `RETENTION`)

On any failure, the trap handler automatically restores from the backup.

---

## Database Migrations (manual)

```bash
# Upgrade to latest schema
MERBANA_DB_URL='sqlite:////absolute/path/to/data/merbana.db' \
python3 -m alembic -c Deployment/backend/alembic.ini upgrade head

# Check current revision
MERBANA_DB_URL='sqlite:////absolute/path/to/data/merbana.db' \
python3 -m alembic -c Deployment/backend/alembic.ini current
```

Always backup `merbana.db`, `merbana.db-wal`, `merbana.db-shm` before running migrations.

---

## Migrate Legacy JSON Data to SQLite

If upgrading from the old JSON-based database:

```bash
python Deployment/migrate_json_to_sqlite.py --source data/db.json --overwrite
```

Reports and validation artifacts are written to `artifacts/`.
