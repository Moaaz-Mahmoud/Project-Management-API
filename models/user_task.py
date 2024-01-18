from sqlalchemy import Column, DateTime, ForeignKey
from db import db


class UserTaskModel(db.Model):
    __tablename__ = "users_tasks"

    user_id = Column(db.String(), ForeignKey('users.id'), primary_key=True)
    task_id = Column(db.String(), ForeignKey('tasks.id'), primary_key=True)

    created_at = Column(DateTime, default=db.func.current_timestamp())
