from flask.views import MethodView
from flask_jwt_extended import jwt_required
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

blp = Blueprint("welfare", __name__, description="Operations on welfare events")


# Welfare endpoints: listing and single-event fetch are public. Creating,
# updating and deleting events require authentication (and can be restricted
# further to admin-only in the future).


@blp.route("/welfare")
class WelfareFunctions(MethodView):
    # Return all welfare events, ordered by date.
    @blp.response(200, schema=WelfareSchema(many=True), description="Get all welfare events")
    def get(self):
        """Get all welfare events"""
        return WelfareModel.query.order_by(WelfareModel.date.asc()).all()

    # Create a new welfare event from the request payload.
    @blp.arguments(WelfareCreateSchema, location="json")
    @blp.response(201, schema=WelfareSchema, description="Create a welfare event")
    @jwt_required()
    def post(self, payload):
        """Create a new welfare event"""
        welfare = WelfareSchema().load(payload, session=db.session)

        db.session.add(welfare)
        db.session.commit()

        return welfare, 201


@blp.route("/welfare/<int:event_id>")
class WelfareEvent(MethodView):
    # Retrieve one welfare event by its ID.
    @blp.response(200, schema=WelfareSchema, description="Get a welfare event by ID")
    def get(self, event_id):
        """Get a welfare event by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare event not found")

        return welfare

    # Update an existing welfare event.
    @blp.arguments(WelfareUpdateSchema, location="json")
    @blp.response(200, schema=WelfareSchema, description="Edit a welfare event")
    @jwt_required()
    def put(self, payload, event_id):
        """Edit a welfare event by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare event not found")

        welfare = WelfareSchema().load(payload, instance=welfare, partial=True, session=db.session)
        db.session.commit()
        return welfare

    # Delete a welfare event by its ID.
    @blp.response(204, description="Delete a welfare event")
    @jwt_required()
    def delete(self, event_id):
        """Delete a welfare event by ID"""
        welfare = WelfareModel.query.get(event_id)
        if not welfare:
            abort(404, message="Welfare event not found")

        db.session.delete(welfare)
        db.session.commit()

        return "", 204
