import os
from dotenv import load_dotenv

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from db import db

from resources.sample_resource import blp as sample_blueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["API_TITLE"] = "Stores REST API"
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
    with app.app_context():
        import models
        db.create_all()
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    api.register_blueprint(sample_blueprint)

    return app
