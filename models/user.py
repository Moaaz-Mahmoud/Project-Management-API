from sqlalchemy import Column, DateTime, ForeignKey, Enum
import enum
import uuid
from db import db


class UserStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(db.String(255), nullable=False)
    username = Column(db.String(255), unique=True, nullable=False)
    email = Column(db.String(255), unique=True, nullable=False)
    password_hash = Column(db.String(), nullable=False)
    role_id = Column(db.String(), ForeignKey('roles.id'), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)

    created_at = Column(DateTime, default=db.func.current_timestamp())
    updated_at = Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
