from sqlalchemy import Column, Enum
import enum
import uuid
from db import db


class PermissionType(enum.Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    ASSIGN_USER = "assign_user"


class PermissionModel(db.Model):
    __tablename__ = "permissions"

    id = Column(db.String(), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    permission = Column(Enum(PermissionType), nullable=False)