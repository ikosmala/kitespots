from .database import Base
from sqlalchemy import Boolean, Column, String, Integer, Float, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import relationship


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
    spots = relationship(
        "Spot", secondary="user_spots", back_populates="users", passive_deletes=True
    )


class Spot(Base):
    __tablename__ = "spots"
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String, nullable=False, unique=True)
    country = Column(String, nullable=False)

    users = relationship(
        "User", secondary="user_spots", back_populates="spots", passive_deletes=True
    )


class UserSpots(Base):
    __tablename__ = "user_spots"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    spot_id = Column(
        Integer, ForeignKey("spots.id", ondelete="CASCADE"), primary_key=True
    )
