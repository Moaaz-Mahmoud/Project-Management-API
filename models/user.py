from sqlalchemy import DateTime, ForeignKey, Enum
import enum
import uuid
from db import db


class UserStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    role_id = db.Column(db.String(), ForeignKey('roles.id'), nullable=False)
    status = db.Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
