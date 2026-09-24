from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session