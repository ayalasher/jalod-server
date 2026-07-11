from flask.views import MethodView
from flask_smorest import Blueprint, abort

try:
    from ..db import db
    from ..models.welfare import WelfareModel
    from ..schemas.welfare import WelfareCreateSchema, WelfareSchema, WelfareUpdateSchema
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
    from models.welfare import WelfareModel
    from schemas.welfare import WelfareCreateSchema, WelfareSchema, WelfareUpdateSchema

# Create the welfare blueprint for API routes.
blp = Blueprint("welfare", __name__, description="Operations on welfare functions")


@blp.route("/welfare")
class WelfareFunctions(MethodView):
    # Return all welfare functions, ordered by date.
    @blp.response(200, schema=WelfareSchema(many=True), description="Get all welfare functions")
    def get(self):
        """Get all welfare functions"""
        return WelfareModel.query.order_by(WelfareModel.date.asc()).all()

    # Create a new welfare function from the request payload.
    @blp.arguments(WelfareCreateSchema, location="json")
    @blp.response(201, schema=WelfareSchema, description="Create a welfare function")
    def post(self, payload):
        """Create a new welfare function"""
        welfare = WelfareSchema().load(payload, session=db.session)

        db.session.add(welfare)
        db.session.commit()

        return welfare, 201


@blp.route("/welfare/<int:event_id>")
class WelfareFunction(MethodView):
    # Retrieve one welfare function by its ID.
    @blp.response(200, schema=WelfareSchema, description="Get a welfare function by ID")
    def get(self, event_id):
        """Get a welfare function by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare function not found")

        return welfare

    # Update an existing welfare function.
    @blp.arguments(WelfareUpdateSchema, location="json")
    @blp.response(200, schema=WelfareSchema, description="Edit a welfare function")
    def put(self, payload, event_id):
        """Edit a welfare function by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare function not found")

        welfare = WelfareSchema().load(payload, instance=welfare, partial=True, session=db.session)
        db.session.commit()
        return welfare

    # Delete a welfare function by its ID.
    @blp.response(204, description="Delete a welfare function")
    def delete(self, event_id):
        """Delete a welfare function by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare function not found")

        db.session.delete(welfare)
        db.session.commit()

        return "", 204
