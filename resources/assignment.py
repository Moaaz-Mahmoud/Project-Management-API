import os

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.user_task_assignment import UserTaskAssignmentModel


blp = Blueprint('Assignments', 'assignments')


@blp.route('/assign')
class UserTaskAssignment(MethodView):
    @jwt_required()
    def post(self):
        user_id = request.args['user_id']
        task_id = request.args['task_id']

        if get_jwt_identity() != user_id and get_jwt_identity() != int(os.getenv('ADMIN_USER_ID')):
            abort(401, message=f'Unauthorized: You do not have permission to access this resource')

        assignment = UserTaskAssignmentModel(user_id=user_id, task_id=task_id)

        try:
            db.session.add(assignment)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()  # Rollback the transaction to avoid partial changes
            abort(409, message=str(e))
        except SQLAlchemyError:
            db.session.rollback()  # Rollback the transaction in case of other database errors
            abort(422)

        return {
            'user_id': user_id,
            'task_id': task_id
        }

    @jwt_required()
    def delete(self):
        user_id = request.args['user_id']
        task_id = request.args['task_id']

        if get_jwt_identity() != user_id and get_jwt_identity() != int(os.getenv('ADMIN_USER_ID')):
            abort(401, message=f'Unauthorized: You do not have permission to access this resource')

        assignment = UserTaskAssignmentModel.query.filter_by(user_id=user_id, task_id=task_id).first()
        if assignment is None:
            abort(404, message='Assignment not found')  # Return a 404 response for non-existing assignment

        try:
            db.session.delete(assignment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()  # Rollback the transaction in case of other database errors
            abort(422)

        return {'message': 'User unassigned successfully'}
