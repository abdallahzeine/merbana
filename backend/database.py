"""
backend/database.py
===================
Database connection and session management.

Provides SQLAlchemy engine configuration with SQLite pragmas,
session factory, and FastAPI dependency for database access.
"""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from .models import Base
from .paths import get_database_url, ensure_data_dir


# SQLite connection string
SQLALCHEMY_DATABASE_URL = get_database_url()

# Create engine with SQLite-specific settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Required for SQLite in multi-threaded apps
    },
    pool_pre_ping=True,  # Verify connections before using from pool
    pool_recycle=300,  # Recycle connections after 5 minutes
)


# Configure SQLite pragmas on connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Set SQLite pragmas for better reliability and performance.

    - foreign_keys=ON: Enforce foreign key constraints
    - journal_mode=WAL: Write-Ahead Logging for better concurrency
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...

    The session is automatically closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once at application startup.
    Creates the data directory if it doesn't exist.
    """
    # Ensure data directory exists
    ensure_data_dir()

    # Create all tables
    Base.metadata.create_all(bind=engine)
