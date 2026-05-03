import psycopg
from fastapi import HTTPException, Request
from sqlalchemy import create_engine

from app.models import metadata


def init_db(dsn: str) -> None:
    # Ensure SQLAlchemy uses the psycopg (psycopg3) dialect instead of
    # defaulting to psycopg2. If the DSN is the generic postgres scheme,
    # rewrite it to explicitly use the psycopg driver.
    sa_dsn = dsn
    if dsn.startswith("postgresql://"):
        sa_dsn = dsn.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(sa_dsn)
    metadata.create_all(engine)


def get_db(request: Request) -> psycopg.Connection:
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    return db
