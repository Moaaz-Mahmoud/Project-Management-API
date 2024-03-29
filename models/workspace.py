from sqlalchemy import DateTime, ForeignKey
from db import db


class WorkspaceModel(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer(), ForeignKey('users.id'), primary_key=True)
    task_id = db.Column(db.Integer(), ForeignKey('tasks.id'), primary_key=True)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
