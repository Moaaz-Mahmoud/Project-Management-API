import os

import psycopg2
from dotenv import load_dotenv
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from psycopg2 import OperationalError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import FlushError, StaleDataError

from constants import GENERIC500
from db import db
from models import TaskModel, UserTaskAssignmentModel
from models.task import TaskStatus
from schemas import TaskSchema

load_dotenv()
database_url = os.getenv('DATABASE_URL')

blp = Blueprint('Tasks', 'tasks')


@blp.route('/users/<int:user_id>/tasks')
class TaskList(MethodView):
    @jwt_required()
    @blp.response(200, TaskSchema(many=True))
    def get(self, user_id):
        try:
            query = '''
                WITH associated_tasks AS (
                    SELECT task_id
                    FROM user_task_assignments
                    WHERE user_id = %s
                )
                SELECT *
                FROM tasks
                WHERE id IN (SELECT task_id FROM associated_tasks)
            '''

            connection = psycopg2.connect(database_url)
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))

            associated_tasks = [row for row in cursor.fetchall()]

            keys = TaskModel.__table__.columns.keys()
            serialized_tasks = [(dict(zip(keys, values))) for values in associated_tasks]

            cursor.close()
            connection.close()

            return serialized_tasks
        except OperationalError as e:
            abort(500, message=f"Database connection error: {str(e)}")
        except psycopg2.Error as e:
            abort(500, message=f"Database error: {str(e)}")
        except Exception as e:
            abort(500, message=f'{GENERIC500}: {str(e)}')

    @jwt_required()
    @blp.arguments(TaskSchema)
    @blp.response(201, TaskSchema)
    def post(self, task_data, user_id):
        try:
            task_data['status'] = TaskStatus(task_data['status'])  # To make it ready for the model
        except ValueError as e:
            abort(400, message=f'Invalid input: {str(e)}')

        try:
            task = TaskModel(**task_data)
            db.session.add(task)
            db.session.commit()

            assignment = UserTaskAssignmentModel(  # Assign to current user
                user_id=user_id,
                task_id=task.id
            )
            db.session.add(assignment)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(409, message=f'Database error: {str(e)}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(422, message=f'Database error: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'{GENERIC500}: {str(e)}')

        task_data['status'] = task_data['status'].value  # For serialization
        return task_data, 201


@blp.route('/tasks/<int:task_id>')
class Task(MethodView):
    @jwt_required()
    @blp.response(200)
    def get(self, task_id):
        task = TaskModel.query.get(task_id)

        if task is None:
            abort(404, message="Task doesn't exist")

        try:
            return task.as_dict()
        except Exception as e:
            abort(400, message=f'{GENERIC500}: {str(e)}')

    @jwt_required()
    @blp.arguments(TaskSchema)
    @blp.response(200)
    def patch(self, task_data, task_id):
        task = TaskModel.query.get(task_id)

        try:
            task_data['status'] = TaskStatus(task_data['status'])  # To make it ready for the model
        except ValueError as e:
            abort(400, message=f'Invalid input: {str(e)}')

        if not task:
            abort(404, message="Task doesn't exist")
        for key, value in task_data.items():
            setattr(task, key, value)

        try:
            db.session.add(task)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f'Error updating task: {str(e)}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(422, message=f'Error updating task: {str(e)}')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"{GENERIC500}: {str(e)}")

        task_data['status'] = task_data['status'].value

        return task_data

    @jwt_required()
    @blp.response(200)
    def delete(self, task_id):
        task = TaskModel.query.get_or_404(task_id)

        if not task:
            abort(404, message="Task doesn't exist")

        try:
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deleted successfully'}
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except (FlushError, InvalidRequestError, StaleDataError) as e:
            db.session.rollback()
            abort(400, message=f'Database error: {str(e)}')
        except Exception as e:
            abort(500, message=f"{GENERIC500}: {str(e)}")
