from sqlalchemy import Column, DateTime, ForeignKey
import uuid
from db import db


class RoleModel(db.Model):
    __tablename__ = "roles"

    id = Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(db.String(), nullable=False)
    permission_id = Column(db.String(), ForeignKey('permissions.id'), nullable=False)

    created_at = Column(DateTime, default=db.func.current_timestamp())
    updated_at = Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
