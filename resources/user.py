import os

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256 as hashing_algo

from db import db
from models import UserModel
from schemas import UserSchema, UserLoginSchema, UserPatchSchema
from utils.admin_privilege_required import admin_privilege_required
from utils.credentials_util import CredentialsUtil
from blocklist import BLOCKLIST


blp = Blueprint('Users', 'users')


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user = UserModel(**user_data)
        user.password = hashing_algo.hash(user.password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=str(e))
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user.")

        return user


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_credentials):
        username_email = user_credentials['username_or_email']
        password = user_credentials['password']
        credential_type = CredentialsUtil.get_credential_type(username_email)

        if credential_type == 'email':
            user = UserModel.query.filter_by(email=username_email).first()
        elif credential_type == 'username':
            user = UserModel.query.filter_by(username=username_email).first()
        else:
            abort(400, message='Invalid username or email')

        if user and hashing_algo.verify(password, user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message='Invalid credentials')


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            return {'message': 'Successfully logged out'}, 200
        except Exception as e:
            abort(500, e)


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200


@blp.route('/users/<int:user_id>')
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        identity = get_jwt_identity()
        if identity == user_id or identity == int(os.getenv('ADMIN_USER_ID')):
            user = UserModel.query.get_or_404(user_id)
            return user
        abort(401, message=f"Unauthorized: You do not have permission to access this resource")

    @jwt_required()
    # @blp.arguments(UserIdArg, location='query')
    @blp.arguments(UserPatchSchema, location='json')
    # @blp.response(200, UserSchema)
    def patch(self, user_data, user_id):
        if user_id == get_jwt_identity() or user_id == int(os.getenv('ADMIN_USER_ID')):
            user = UserModel.query.get_or_404(user_id)
        else:
            abort(401, message="Unauthorized: You do not have permission to access this resource")

        try:
            for key, value in user_data.items():
                setattr(user, key, value)
        except KeyError as e:
            abort(400, message=str(e))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=str(e))
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user.")

        return user_data

    @jwt_required()
    @blp.response(200, UserSchema)
    def delete(self, user_id):
        if user_id != get_jwt_identity() and user_id != int(os.getenv('ADMIN_USER_ID')):
            abort(401, message="Unauthorized: You do not have permission to access this resource")

        user = UserModel.query.filter_by(id=user_id).first()

        if not user:
            abort(404, message="User doesn't exist")

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}
        except SQLAlchemyError:
            abort(404, message='Error deleting user')


@blp.route('/users/all')
class UserList(MethodView):
    @jwt_required()
    @admin_privilege_required
    @blp.response(200, UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users
