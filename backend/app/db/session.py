"""SQLAlchemy engine and session factory for PostgreSQL."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

database_url = make_url(settings.DATABASE_URL)

# psycopg3 starts caching server-side prepared statements after five repeats.
# A pooled proxy such as Supabase's transaction pooler routes successive
# queries to different backends, so the statement is gone when it is reused
# and every read endpoint starts erroring. Only PostgreSQL accepts the option.
connect_args = {"prepare_threshold": 0} if database_url.get_backend_name() == "postgresql" else {}

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
