from sqlalchemy import DateTime, ForeignKey
import uuid
from db import db


class RoleModel(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    permission_id = db.Column(db.String(), ForeignKey('permissions.id'), nullable=False)

    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
