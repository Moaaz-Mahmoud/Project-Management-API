from sqlalchemy import DateTime, ForeignKey
from db import db


class UserTaskAssignmentModel(db.Model):
    __tablename__ = "user_task_assignments"

    id = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String(), ForeignKey('users.id'))
    task_id = db.Column(db.String(), ForeignKey('tasks.id'))

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
