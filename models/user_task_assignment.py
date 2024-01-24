from sqlalchemy import DateTime, ForeignKey
from db import db


class UserTaskModel(db.Model):
    __tablename__ = "users_tasks"

    user_id = db.Column(db.String(), ForeignKey('users.id'), primary_key=True)
    task_id = db.Column(db.String(), ForeignKey('tasks.id'), primary_key=True)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
