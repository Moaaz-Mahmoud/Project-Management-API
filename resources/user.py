import os

from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended.exceptions import JWTDecodeError
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound, InvalidRequestError
from passlib.hash import pbkdf2_sha256 as hashing_algo
from sqlalchemy.orm.exc import FlushError, StaleDataError

from constants import GENERIC500
from db import db
from models import UserModel
from models.user import UserStatus
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
        try:
            user = UserModel(**user_data)
            user.password = hashing_algo.hash(user.password)
        except Exception as e:
            abort(500, message=f'{GENERIC500}: {str(e)}')

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(409, message=f'Database error: {str(e)}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'{GENERIC500}: {str(e)}')

        return user


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(200)
    def post(self, user_credentials):
        username_email = user_credentials.get('username_or_email')
        password = user_credentials.get('password')
        credential_type = CredentialsUtil.get_credential_type(username_email)

        try:
            if credential_type == 'email':
                user = UserModel.query.filter_by(email=username_email).first()
            elif credential_type == 'username':
                user = UserModel.query.filter_by(username=username_email).first()
            else:
                abort(400, message='Invalid username or email.')

            if user and hashing_algo.verify(password, user.password):
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
        except KeyError as e:
            abort(400, message=f'Missing key in user_credentials: {str(e)}')
        except SQLAlchemyError as e:
            abort(500, message=f'Database error: {str(e)}')
        except ValueError as e:
            abort(400, message=f'Invalid value: {str(e)}')
        except Exception as e:
            abort(500, message=f'{GENERIC500}: {str(e)}')

        abort(401, message='Invalid credentials')


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200)
    def post(self):
        try:
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            return {'message': 'Successfully logged out'}
        except (JWTDecodeError, ExpiredSignatureError, InvalidTokenError):
            abort(401, message='Not logged in.')
        except Exception as e:
            abort(500, message=f'{GENERIC500}: {str(e)}')


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200)
    def post(self):
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user, fresh=False)
            # Make it clear that when to add the refresh token to the blocklist will depend on the app design
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            return {"access_token": new_token}
        except (JWTDecodeError, ExpiredSignatureError, InvalidTokenError):
            abort(401, message='Invalid or expired token. Please log in again.')
        except Exception as e:
            abort(500, message=f'{GENERIC500}: {str(e)}')


@blp.route('/users/<int:user_id>')
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        identity = get_jwt_identity()

        try:
            if identity == user_id or identity == int(os.getenv('ADMIN_USER_ID')):
                user = UserModel.query.get_or_404(user_id)
                return user
            abort(401, message=f"Unauthorized: You do not have permission to access this resource")
        except NoResultFound:
            abort(404, message="User not found")
        except Exception as e:
            abort(500, message=f"{GENERIC500}: {str(e)}")

    @jwt_required()
    @blp.arguments(UserPatchSchema, location='json')
    @blp.response(200)
    def patch(self, user_data, user_id):
        if get_jwt_identity() == int(user_id) or get_jwt_identity() == int(os.getenv('ADMIN_USER_ID')):
            user = UserModel.query.get_or_404(user_id)
        else:
            abort(401, message="Unauthorized: You do not have permission to access this resource")

        try:
            user_data['status'] = UserStatus(user_data['status'])
        except KeyError:  # Key doesn't exist? It's optional anyway
            pass

        try:
            for key, value in user_data.items():
                setattr(user, key, value)
        except KeyError as e:
            abort(400, message=str(e))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(409, message=f'Database error: {str(e)}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'{GENERIC500}: {str(e)}')

        try:
            user_data['status'] = user_data['status'].value
        except KeyError:  # Key doesn't exist? It's optional anyway
            pass

        return user_data

    @jwt_required()
    @blp.response(200, UserSchema)
    def delete(self, user_id):
        if get_jwt_identity() == int(user_id) or get_jwt_identity() == int(os.getenv('ADMIN_USER_ID')):
            user = UserModel.query.get_or_404(user_id)
        else:
            abort(401, message="Unauthorized: You do not have permission to access this resource")

        if not user:
            abort(404, message="User doesn't exist")

        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except (FlushError, InvalidRequestError, StaleDataError) as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except Exception as e:
            abort(500, message=f"{GENERIC500}: {str(e)}")


@blp.route('/users/all')
class UserList(MethodView):
    @jwt_required()
    @admin_privilege_required
    @blp.response(200, UserSchema(many=True))
    def get(self):
        try:
            users = UserModel.query.all()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"{GENERIC500}: {str(e)}")

        return users
