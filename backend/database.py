from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(f"{settings.pg_dsn}")

SessionLocal = sessionmaker(autocommit=False, bind=engine, autoflush=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
