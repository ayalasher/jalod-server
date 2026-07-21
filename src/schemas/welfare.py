from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

try:
    from ..db import db
    from ..models.welfare import WelfareModel
    from .member import BirthdaySchema
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
    from models.welfare import WelfareModel
    from schemas.member import BirthdaySchema


class WelfareSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WelfareModel
        load_instance = True
        sqla_session = db.session

    event_id = fields.Int(required=True)
    event_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    date = fields.DateTime(required=True)
    description = fields.String(allow_none=True)
    amount_spent = fields.Decimal(allow_none=True)
    status = fields.String(required=True, validate=validate.OneOf(["Done", "Not Completed"]))


class WelfareCreateSchema(Schema):
    event_id = fields.Int(required=True)
    event_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    date = fields.DateTime(required=True)
    description = fields.String(allow_none=True)
    amount_spent = fields.Decimal(allow_none=True)
    status = fields.String(required=True, validate=validate.OneOf(["Done", "Not Completed"]))


class WelfareUpdateSchema(Schema):
    event_id = fields.Int()
    event_name = fields.String(validate=validate.Length(min=2, max=100))
    date = fields.DateTime()
    description = fields.String(allow_none=True)
    amount_spent = fields.Decimal(allow_none=True)
    status = fields.String(validate=validate.OneOf(["Done", "Not Completed"]))


class WelfareMonthResponseSchema(Schema):
    """Response schema for welfare events + birthdays in a month."""
    events = fields.List(fields.Nested(WelfareSchema))
    birthdays = fields.List(fields.Nested(BirthdaySchema))
