"""
build_windows.py
================
Build the Merbana Windows distributable.

Steps
-----
1. npm run build -> produces ./dist (React SPA)
2. PyInstaller --onefile -> compiles Deployment/merbana_launcher.py into ./dist_windows/Merbana.exe

This script does not run migrations automatically. Operator must run Alembic upgrade
using MERBANA_DB_URL before starting the packaged app after schema changes.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run(cmd: str | list[str], *, cwd: Path | None = None) -> None:
    """Run a command and exit if it fails."""
    display = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f"\n> {display}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd)
    if result.returncode != 0:
        print(f"\nCommand failed with exit code {result.returncode}")
        raise SystemExit(result.returncode)


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found, installing...")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def print_migration_operator_steps(project_root: Path) -> None:
    """Print explicit migration operator commands for Windows."""
    alembic_ini = project_root / "Deployment" / "backend" / "alembic.ini"
    print("\nMigration operator step (required before app startup):")
    print("  1) Backup SQLite files: merbana.db, merbana.db-wal, merbana.db-shm")
    print("  2) PowerShell:")
    print("     $env:MERBANA_DB_URL='sqlite:///C:/Path/To/data/merbana.db'")
    print(
        "     python -m alembic -c "
        f"{alembic_ini} upgrade head"
    )


def main() -> None:
    if platform.system() != "Windows":
        print(f"This script must run on Windows. Detected: {platform.system()}")
        raise SystemExit(1)

    parser = argparse.ArgumentParser(description="Build Merbana Windows distributable")
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip npm run build and reuse existing dist",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    deployment_dir = project_root / "Deployment"
    launcher_script = deployment_dir / "merbana_launcher.py"
    dist_web = project_root / "dist"
    out_dir = project_root / "dist_windows"
    output_exe = out_dir / "Merbana.exe"

    pi_build_dir = project_root / "build_pyinstaller"
    spec_file = project_root / "Merbana.spec"

    t_start = time.time()
    print("=" * 60)
    print("Merbana Windows Build Script")
    print(f"Project root: {project_root}")
    print("=" * 60)

    if args.skip_frontend:
        if not (dist_web / "index.html").exists():
            print("dist/index.html not found; run without --skip-frontend first.")
            raise SystemExit(1)
    else:
        if dist_web.exists():
            shutil.rmtree(dist_web)
        run("npm run build", cwd=project_root)
        if not (dist_web / "index.html").exists():
            print("Frontend build failed: dist/index.html not found.")
            raise SystemExit(1)

    ensure_pyinstaller()

    if out_dir.exists():
        shutil.rmtree(out_dir)

    for path in (pi_build_dir, spec_file):
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    add_data = f"{dist_web};dist"

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--add-data",
        add_data,
        "--name",
        "Merbana",
        "--distpath",
        str(out_dir),
        "--workpath",
        str(pi_build_dir),
        "--specpath",
        str(project_root),
        "--hidden-import",
        "webview",
        "--hidden-import",
        "webview.http",
        str(launcher_script),
    ]

    run(pyinstaller_cmd, cwd=project_root)

    if not output_exe.exists():
        print(f"Build finished but expected output was not found: {output_exe}")
        raise SystemExit(1)

    size_mb = output_exe.stat().st_size / (1024 * 1024)
    elapsed = time.time() - t_start

    print("\n" + "=" * 60)
    print("Windows build complete")
    print(f"Binary: {output_exe}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Time: {elapsed:.0f}s")
    print("=" * 60)

    print_migration_operator_steps(project_root)

    for path in (pi_build_dir, spec_file):
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


if __name__ == "__main__":
    main()
