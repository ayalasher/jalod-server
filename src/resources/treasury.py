from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

blp = Blueprint("treasury", __name__, description="Operations on treasury")


def _ensure_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        abort(403, message="Admin privileges required")


@blp.route("/treasury")
class Treasury(MethodView):
    @blp.response(200, description="Get all treasury data")
    @jwt_required()
    def get(self):
        _ensure_admin()
        """Get all treasury data"""
        return []
