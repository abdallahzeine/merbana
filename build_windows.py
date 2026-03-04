"""
build_windows.py
================
Builds Merbana into a self-contained Windows distribution folder.

Output layout (dist_windows/)
------------------------------
    Merbana.bat      ← double-click this to launch the app
    Merbana.exe      ← compiled Python launcher (PyInstaller onefile)
    dist/            ← React SPA served at runtime
    data/
        db.json      ← persistent database

How it works
------------
Merbana.exe is built with PyInstaller --onefile from Deployment/merbana_launcher.py.
The React dist/ folder is placed NEXT TO the exe (not embedded inside it), and
Merbana.bat sets the MERBANA_DIST_PATH environment variable so the launcher
finds it correctly — the same pattern used by build_pos.sh on Linux.

Usage
-----
    python build_windows.py [--skip-frontend]

Requirements
------------
    pip install pyinstaller pywebview
    Node.js >= 18  (npm in PATH)

Options
-------
    --skip-frontend   Reuse an existing dist/ folder, skip npm run build
    --out DIR         Output directory (default: dist_windows)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────────────────────────

def run(cmd: str | list, *, cwd: Path | None = None) -> None:
    """Run a command; exit the script on non-zero return code."""
    display = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f"\n▶  {display}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd)
    if result.returncode != 0:
        print(f"\n✗  Command failed (exit {result.returncode})")
        sys.exit(result.returncode)


def ensure_pyinstaller() -> None:
    """Install PyInstaller if it is not already available."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found — installing …")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def check_pywebview() -> None:
    """Warn if pywebview is missing (app falls back to browser, but native window won't work)."""
    try:
        import webview  # noqa: F401
    except ImportError:
        print(
            "\n⚠  pywebview not found — the app will open in the default browser instead\n"
            "   of a native window.  To enable the native window:\n"
            "       pip install pywebview\n"
        )


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if platform.system() != "Windows":
        print(
            "⚠  This script is for Windows only.\n"
            "   You are on: " + platform.system() + "\n"
            "   For Linux use:  bash Deployment/build_pos.sh\n"
            "                or python Deployment/build_linux.py"
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Build Merbana Windows distribution")
    parser.add_argument(
        "--skip-frontend", action="store_true",
        help="Skip 'npm run build' and reuse the existing dist/ folder",
    )
    parser.add_argument(
        "--out", default="dist_windows",
        help="Output directory name (default: dist_windows)",
    )
    args = parser.parse_args()

    project_root   = Path(__file__).parent.resolve()
    deployment_dir = project_root / "Deployment"
    launcher_src   = deployment_dir / "merbana_launcher.py"
    dist_web       = project_root / "dist"          # Vite / npm run build output
    data_src       = project_root / "public" / "data"
    out_dir        = project_root / args.out

    t_start = time.time()

    print()
    print("=" * 62)
    print("  Merbana — Windows Build Script")
    print(f"  Project : {project_root}")
    print(f"  Output  : {out_dir}")
    print("=" * 62)

    if not launcher_src.exists():
        print(f"✗  Launcher not found: {launcher_src}")
        sys.exit(1)

    # ── Step 1: React frontend ─────────────────────────────────────────────────
    if args.skip_frontend:
        print("\n⏭  Skipping frontend build (--skip-frontend)")
        if not (dist_web / "index.html").exists():
            print("✗  dist/index.html not found — run without --skip-frontend first.")
            sys.exit(1)
        print(f"✓  Using existing {dist_web}")
    else:
        if dist_web.exists():
            print(f"\n🧹 Cleaning {dist_web} …")
            shutil.rmtree(dist_web)

        print("\n⚛  Building React frontend …")
        run("npm run build", cwd=project_root)

        if not (dist_web / "index.html").exists():
            print("✗  Frontend build failed: dist/index.html not found.")
            sys.exit(1)
        print("✓  Frontend build OK")

    # ── Step 2: Ensure tools ───────────────────────────────────────────────────
    ensure_pyinstaller()
    check_pywebview()

    # ── Step 3: Clean output dir ───────────────────────────────────────────────
    if out_dir.exists():
        print(f"\n🧹 Cleaning {out_dir} …")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # PyInstaller work folders (cleaned after build)
    pi_work_dir = project_root / "build_pyinstaller"
    spec_file   = project_root / "Merbana.spec"

    # ── Step 4: Compile exe with PyInstaller ───────────────────────────────────
    print("\n📦 Compiling Merbana.exe with PyInstaller …")

    # dist/ is embedded inside the exe via --add-data so the launcher finds it
    # via sys._MEIPASS when Merbana.exe is run directly.
    # Merbana.bat also sets MERBANA_DIST_PATH (checked first by the launcher)
    # so the external dist/ copy is used when launched via the bat — this
    # avoids the overhead of extracting the embedded copy every startup.
    # On Windows PyInstaller --add-data uses a semicolon: "src;dest"
    add_data = f"{dist_web};dist"

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",                        # no console window
        "--name", "Merbana",
        "--distpath", str(out_dir),           # put Merbana.exe straight into out_dir
        "--workpath", str(pi_work_dir),
        "--specpath", str(project_root),
        "--add-data", add_data,               # embed dist/ so _MEIPASS/dist exists
        # Hidden imports so PyInstaller bundles everything the launcher needs
        "--hidden-import", "webview",
        "--hidden-import", "webview.http",
        "--hidden-import", "webview.platforms.winforms",
        "--hidden-import", "clr",
        str(launcher_src),
    ]

    run(pyinstaller_cmd, cwd=project_root)

    exe_path = out_dir / "Merbana.exe"
    if not exe_path.exists():
        print(f"✗  Compilation succeeded but {exe_path} was not found.")
        sys.exit(1)
    print(f"✓  Merbana.exe  ({exe_path.stat().st_size / 1_048_576:.1f} MB)")

    # ── Step 5: Copy React build ───────────────────────────────────────────────
    print("\n📂 Copying dist/ …")
    shutil.copytree(dist_web, out_dir / "dist")
    print(f"✓  dist/ copied")

    # ── Step 6: Copy database ──────────────────────────────────────────────────
    out_data = out_dir / "data"
    if data_src.exists():
        print("\n💾 Copying data/ …")
        shutil.copytree(data_src, out_data)
        print(f"✓  data/ copied")
    else:
        # Create a minimal empty db.json if the source doesn't exist
        print("\n💾 Creating empty data/db.json …")
        out_data.mkdir(parents=True)
        (out_data / "db.json").write_text(
            '{"products":[],"categories":[],"orders":[],'
            '"register":{"currentBalance":0,"transactions":[]},'
            '"users":[],"activityLog":[],"settings":{"companyName":""},'
            '"debtors":[],"lastStockReset":""}',
            encoding="utf-8",
        )
        print("✓  data/db.json created (empty)")

    # ── Step 7: Create Merbana.bat launcher ────────────────────────────────────
    # Sets MERBANA_DIST_PATH to the dist/ folder next to the bat, which the
    # launcher checks before any other path resolution — same pattern as the
    # Linux shell wrapper in build_pos.sh.
    print("\n📝 Creating Merbana.bat …")
    bat_path = out_dir / "Merbana.bat"
    bat_path.write_text(
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "set MERBANA_DIST_PATH=%~dp0dist\r\n"
        "start \"\" \"%~dp0Merbana.exe\"\r\n",
        encoding="utf-8",
    )
    print("✓  Merbana.bat created")

    # ── Step 8: Clean PyInstaller work artefacts ───────────────────────────────
    for path in (pi_work_dir, spec_file):
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # ── Done ───────────────────────────────────────────────────────────────────
    elapsed = time.time() - t_start
    total_size_mb = sum(
        f.stat().st_size for f in out_dir.rglob("*") if f.is_file()
    ) / 1_048_576

    print()
    print("=" * 62)
    print("  ✅  Build complete!")
    print(f"  Output  : {out_dir}\\")
    print(f"    Merbana.bat   ← double-click to launch")
    print(f"    Merbana.exe   ← compiled launcher")
    print(f"    dist/         ← React app")
    print(f"    data/         ← database (db.json)")
    print(f"  Total size : {total_size_mb:.1f} MB")
    print(f"  Time       : {elapsed:.0f}s")
    print("=" * 62)
    print()
    print("  To distribute: copy the entire dist_windows/ folder.")
    print("  Users double-click Merbana.bat to start the app.")
    print()


if __name__ == "__main__":
    main()
