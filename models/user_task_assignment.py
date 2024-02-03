from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from db import db


class UserTaskAssignmentModel(db.Model):
    __tablename__ = "user_task_assignments"

    id = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer(), ForeignKey('users.id', ondelete='CASCADE'))
    task_id = db.Column(db.Integer(), ForeignKey('tasks.id', ondelete='CASCADE'))

    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    __table_args__ = (
        UniqueConstraint('user_id', 'task_id', name='_user_task_uc'),
    )
