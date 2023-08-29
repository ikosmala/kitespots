from .database import Base
from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.functions import func


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(
        String,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
