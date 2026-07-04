from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("contributions", __name__, description="Operations on contributions")


@blp.route("/contributions")
class Contributions(MethodView):
    @blp.response(200, description="Get all contributions")
    def get(self):
        """Get all contributions"""
        return []
