from sqlalchemy import DateTime, Enum
import enum
import uuid
from db import db


class TaskStatus(enum.Enum):
    TODO = "todo"
    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String())
    due_date = db.Column(DateTime)
    status = db.Column(Enum(TaskStatus), nullable=False)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
