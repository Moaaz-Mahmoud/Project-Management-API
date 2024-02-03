import json
import os

from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256 as hashing_algo

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from db import db
from blocklist import BLOCKLIST

import logging

from models import UserModel, TaskModel, UserTaskAssignmentModel
from models.user import UserStatus
from resources.sample_resource import blp as sample_blueprint
from resources.user import blp as user_blueprint
from resources.task import blp as task_blueprint
from resources.assignment import blp as assignment_blueprint


def create_app(db_url=None):
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    app.config["API_TITLE"] = "Project Management REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL")
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)

    @app.cli.command('db_create')
    def db_create():
        with app.app_context():
            db.create_all()

    @app.cli.command('db_seed')
    def db_seed():
        with app.app_context():
            with db.session.begin():
                with open('seed_data.json', 'r') as file:
                    data = json.load(file)
                    users = data['users']
                    tasks = data['tasks']
                    assignments = data['assignments']

                for user_data in users:
                    user = UserModel(
                        name=user_data['name'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password=hashing_algo.hash(user_data['password']),
                        status=UserStatus[user_data['status'].upper()]  # Convert string to Enum
                    )
                    db.session.add(user)

                for task_data in tasks:
                    task = TaskModel(
                        name=task_data['name'],
                        description=task_data['description'],
                        due_date=task_data['due_date'],
                        status=task_data['status']
                    )
                    db.session.add(task)

                for assignment_data in assignments:
                    assignment = UserTaskAssignmentModel(
                        user_id=assignment_data['user_id'],
                        task_id=assignment_data['task_id'],
                    )
                    db.session.add(assignment)

                db.session.commit()

    api = Api(app)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    api.register_blueprint(sample_blueprint)
    api.register_blueprint(user_blueprint)
    api.register_blueprint(task_blueprint)
    api.register_blueprint(assignment_blueprint)

    return app
