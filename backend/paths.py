"""
backend/paths.py
================
Path resolution utilities for the Merbana backend.

Handles both packaged (PyInstaller) and development modes.
Extracted from merbana_launcher.py for reuse across the backend.
"""

import os
import sys
from pathlib import Path


def is_packaged() -> bool:
    """Check if running in a PyInstaller packaged environment."""
    return getattr(sys, "_MEIPASS", None) is not None


def get_dist_path() -> str:
    """
    Return the path to the React dist/ folder.

    Resolution order:
    1. MERBANA_DIST_PATH environment variable
    2. PyInstaller _MEIPASS directory
    3. Development: project_root/dist
    """
    # 1. Explicit env var (set by Merbana.bat / shell wrapper)
    env = os.environ.get("MERBANA_DIST_PATH", "")
    if env and os.path.isdir(env):
        return env

    # 2. PyInstaller onefile (_MEIPASS/dist)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return os.path.join(meipass, "dist")

    # 3. Plain script: resolve from backend/paths.py location
    # backend/paths.py -> backend/ -> project_root/dist
    backend_dir = Path(__file__).parent.absolute()
    project_root = backend_dir.parent
    return str(project_root / "dist")


def get_data_path() -> str:
    """
    Return the path to the data directory.

    When frozen by PyInstaller (onefile), _MEIPASS is the temp extraction
    directory that is deleted on exit — the data folder must live next to the
    executable instead. In plain-script mode, keep the old behaviour of
    looking one level above dist/.
    """
    env_data_path = os.environ.get("MERBANA_DATA_PATH", "")
    if env_data_path:
        return env_data_path

    if is_packaged():
        # Packaged exe: place data/ beside the .exe so it survives restarts.
        return os.path.join(os.path.dirname(sys.executable), "data")

    # Development: data/ folder at project root
    backend_dir = Path(__file__).parent.absolute()
    project_root = backend_dir.parent
    return str(project_root / "data")


def get_sqlite_db_path(filename: str = "merbana.db") -> str:
    """
    Return the full path to the SQLite database file.

    The database is stored in the data directory.

    Args:
        filename: Name of the database file (default: merbana.db)
    """
    data_dir = get_data_path()
    return os.path.join(data_dir, filename)


def get_database_url() -> str:
    """
    Return the SQLAlchemy database URL used by both runtime and CLI tools.

    Resolution order:
    1. MERBANA_DB_URL environment variable
    2. SQLite URL derived from the resolved data path
    """
    env_db_url = os.environ.get("MERBANA_DB_URL", "").strip()
    if env_db_url:
        return env_db_url

    sqlite_path = Path(get_sqlite_db_path()).resolve().as_posix()
    return f"sqlite:///{sqlite_path}"


def ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist."""
    data_dir = get_data_path()
    os.makedirs(data_dir, exist_ok=True)
