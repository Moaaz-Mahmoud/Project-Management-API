from flask.views import MethodView
from flask_smorest import Blueprint, abort


blp = Blueprint("Sample", import_name='sample_blueprint', description="Sample resource")


@blp.route('/sample')
class SampleResource(MethodView):
    # @blp.response(200)
    def get(self):
        return {'Meow': 'll'}
