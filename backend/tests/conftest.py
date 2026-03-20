"""Shared pytest fixtures for backend API and service tests."""

from typing import Generator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app as app_module
import backend.database as database_module
from backend.app import create_app
from backend.dependencies import get_db
from backend.models import Base


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine with FK enforcement."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    yield engine
    engine.dispose()


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db, monkeypatch):
    """Create a TestClient fully pinned to the in-memory test DB."""
    monkeypatch.setattr(database_module, "SessionLocal", lambda: test_db)

    app = create_app()

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "TestUser",
        "password": "hashed_password_123",
        "created_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "Beverages",
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "name": "TestCoffee",
        "price": 3.50,
        "category_id": None,
        "created_at": "2024-01-15T10:30:00Z",
        "sizes": [
            {
                "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "name": "Small",
                "price": 0.50,
                "sort_order": 1,
            }
        ],
    }
