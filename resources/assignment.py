import os

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import FlushError, StaleDataError

from constants import GENERIC500
from db import db
from models.user_task_assignment import UserTaskAssignmentModel


blp = Blueprint('Assignments', 'assignments')


@blp.route('/assign')
class UserTaskAssignment(MethodView):
    @jwt_required()
    @blp.response(201)
    def post(self):
        user_id = request.args['user_id']
        task_id = request.args['task_id']

        if get_jwt_identity() != user_id and get_jwt_identity() != int(os.getenv('ADMIN_USER_ID')):
            abort(401, message=f'Unauthorized: You do not have permission to access this resource')

        assignment = UserTaskAssignmentModel(user_id=user_id, task_id=task_id)

        try:
            db.session.add(assignment)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message=f'User #{user_id} already assigned to task #{task_id}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(422, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'{GENERIC500}: {str(e)}')

        return {
            'user_id': user_id,
            'task_id': task_id
        }

    @jwt_required()
    @blp.response(200)
    def delete(self):
        user_id = request.args['user_id']
        task_id = request.args['task_id']

        if get_jwt_identity() != user_id and get_jwt_identity() != int(os.getenv('ADMIN_USER_ID')):
            abort(401, message=f'Unauthorized: You do not have permission to access this resource')

        assignment = UserTaskAssignmentModel.query.filter_by(user_id=user_id, task_id=task_id).first_or_404()

        try:
            db.session.delete(assignment)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except SQLAlchemyError:
            db.session.rollback()
            abort(422)
        except (FlushError, InvalidRequestError, StaleDataError) as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'{GENERIC500}: {str(e)}')

        return {'message': 'User unassigned successfully'}
