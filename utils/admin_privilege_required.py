import os
from flask_jwt_extended import get_jwt_identity
from flask_smorest import abort


def admin_privilege_required(func):
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        admin_id = int(os.getenv('ADMIN_USER_ID'))
        if current_user != admin_id:
            func(*args, **kwargs)
            abort(
                401,
                message=f'Admin privilege required',
            )
        return func(*args, **kwargs)

    return wrapper
