from marshmallow import Schema, fields

from models.task import TaskStatus
from models.user import UserStatus


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    status = fields.Enum(UserStatus, required=False)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    due_date = fields.DateTime(required=False)
    status = fields.Enum(TaskStatus, required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class TaskAssignmentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True, load_only=True)
    task_id = fields.Int(required=True, load_only=True)
    created_at = fields.DateTime()


class WorkspaceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    user_id = fields.Int(required=True, load_only=True)
    task_id = fields.Int(required=True, load_only=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserLoginSchema(Schema):
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True)


class UserPatchSchema(Schema):
    name = fields.Str(required=False)
    username = fields.Str(required=False)
    email = fields.Str(required=False)
    password = fields.Str(required=False, load_only=True)
    status = fields.Enum(UserStatus, required=False, default=UserStatus.PENDING)


class UserIdArg(Schema):
    id = fields.Int()
