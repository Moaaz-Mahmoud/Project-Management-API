from marshmallow import Schema, fields

from models.task import TaskStatus
from models.user import UserStatus


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password_hash = fields.Str(required=True, load_only=True)
    status = fields.Enum(UserStatus, required=True, default=UserStatus.PENDING)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserSchema(PlainUserSchema):
    workspace_id = fields.Int(required=True)
    # tasks = fields.List(fields.Nested(PlainTaskSchema()), dump_only=True)


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    due_date = fields.DateTime(required=False)
    status = fields.Enum(TaskStatus, required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
