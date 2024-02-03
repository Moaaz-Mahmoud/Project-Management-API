from collections import defaultdict
from datetime import datetime

from sqlalchemy import DateTime, Enum
import enum

from sqlalchemy.orm import relationship

from db import db


class TaskStatus(enum.Enum):
    TODO = "todo"
    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(), nullable=True, default='')
    due_date = db.Column(DateTime, nullable=True)
    status = db.Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    assignments = relationship('UserTaskAssignmentModel', cascade='all, delete-orphan', backref='task')

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
