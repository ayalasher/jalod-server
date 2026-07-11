from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("treasury", __name__, description="Operations on treasury")


@blp.route("/treasury")
class Treasury(MethodView):
    @blp.response(200, description="Get all treasury data")
    def get(self):
        """Get all treasury data"""
        return []
