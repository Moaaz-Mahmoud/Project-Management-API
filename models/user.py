from collections import defaultdict
from datetime import datetime

from sqlalchemy import DateTime, Enum
import enum

from sqlalchemy.orm import relationship

from db import db


class UserStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    status = db.Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    # workspace_id = db.Column(db.Integer(), ForeignKey('workspaces.id'), nullable=True, default=None)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    assignments = relationship('UserTaskAssignmentModel', cascade='all, delete-orphan', backref='user')

    def as_dict(self):
        object_as_dict = defaultdict()
        for key in self.__table__.columns:
            value = getattr(self, key.name)
            if isinstance(value, enum.Enum):
                value = value.value
            elif isinstance(value, datetime):
                value = value.isoformat()
            object_as_dict[key.name] = value

        return object_as_dict
