"""
backend/tests/test_paths.py
============================
Tests for path resolution utilities.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.paths import (
    is_packaged,
    get_dist_path,
    get_data_path,
    get_sqlite_db_path,
    ensure_data_dir,
)


class TestIsPackaged:
    """Tests for is_packaged function."""

    def test_is_packaged_in_development(self):
        """Test that is_packaged returns False in development mode."""
        assert is_packaged() is False

    def test_is_packaged_with_meipass(self):
        """Test that is_packaged returns True when _MEIPASS is set."""
        original_meipass = getattr(sys, "_MEIPASS", None)
        try:
            sys._MEIPASS = "/tmp/meipass"
            assert is_packaged() is True
        finally:
            if original_meipass is None:
                delattr(sys, "_MEIPASS")
            else:
                sys._MEIPASS = original_meipass


class TestGetDistPath:
    """Tests for get_dist_path function."""

    def test_get_dist_path_development_mode(self):
        """Test get_dist_path returns correct path in development mode."""
        dist_path = get_dist_path()

        assert dist_path.endswith("dist") or dist_path.endswith("dist" + os.sep)

    def test_get_dist_path_with_env_variable(self):
        """Test get_dist_path respects MERBANA_DIST_PATH environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MERBANA_DIST_PATH"] = tmpdir

            try:
                result = get_dist_path()
                assert result == tmpdir
            finally:
                del os.environ["MERBANA_DIST_PATH"]

    def test_get_dist_path_with_meipass(self):
        """Test get_dist_path returns correct path in packaged mode."""
        original_meipass = getattr(sys, "_MEIPASS", None)
        try:
            sys._MEIPASS = "/tmp/meipass"
            dist_path = get_dist_path()
            # FIXED: Normalize path separators before checking
            normalized_path = dist_path.replace("\\", "/")
            assert "/tmp/meipass/dist" in normalized_path
        finally:
            if original_meipass is None:
                delattr(sys, "_MEIPASS")
            else:
                sys._MEIPASS = original_meipass


class TestGetDataPath:
    """Tests for get_data_path function."""

    def test_get_data_path_development_mode(self):
        """Test get_data_path returns correct path in development mode."""
        data_path = get_data_path()

        assert "data" in data_path

    def test_get_data_path_packaged_mode(self):
        """Test get_data_path returns correct path in packaged mode."""
        original_meipass = getattr(sys, "_MEIPASS", None)
        original_executable = sys.executable

        try:
            sys._MEIPASS = "/tmp/meipass"
            sys.executable = "/opt/merbana/Merbana"
            data_path = get_data_path()
            assert "data" in data_path
        finally:
            if original_meipass is None:
                if hasattr(sys, "_MEIPASS"):
                    delattr(sys, "_MEIPASS")
            else:
                sys._MEIPASS = original_meipass
            sys.executable = original_executable


class TestGetSqliteDbPath:
    """Tests for get_sqlite_db_path function."""

    def test_get_sqlite_db_path_default_filename(self):
        """Test get_sqlite_db_path with default filename."""
        path = get_sqlite_db_path()

        assert path.endswith("merbana.db")

    def test_get_sqlite_db_path_custom_filename(self):
        """Test get_sqlite_db_path with custom filename."""
        path = get_sqlite_db_path("custom.db")

        assert path.endswith("custom.db")

    def test_get_sqlite_db_path_includes_data_dir(self):
        """Test that db path is inside data directory."""
        path = get_sqlite_db_path()
        data_dir = get_data_path()

        assert data_dir in path


class TestEnsureDataDir:
    """Tests for ensure_data_dir function."""

    def test_ensure_data_dir_creates_directory(self):
        """Test that ensure_data_dir creates the data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("backend.paths.get_data_path", return_value=tmpdir):
                ensure_data_dir()

                assert os.path.isdir(tmpdir)

    def test_ensure_data_dir_idempotent(self):
        """Test that ensure_data_dir is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "data")

            with patch("backend.paths.get_data_path", return_value=data_path):
                ensure_data_dir()
                ensure_data_dir()

                assert os.path.isdir(data_path)
