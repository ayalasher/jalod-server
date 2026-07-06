from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

try:
    from ..db import db
    from ..models.member import memberModel
    from . import ma
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
    from models.member import memberModel
    from schemas import ma


class MemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = memberModel
        load_instance = True
        sqla_session = db.session
        exclude = (
            "password_hash",
            "contributions_tier",
            "contributions_debt",
            "loans_debt",
            "contributions_dated_at",
        )

    name = fields.String(required=True, validate=validate.Length(min=2, max=40))
    email_address = fields.Email(required=True, validate=validate.Length(max=40))
    phone_number = fields.Integer(required=True)
    birthday = fields.DateTime(allow_none=True)


class MemberCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=40))
    email_address = fields.Email(required=True, validate=validate.Length(max=40))
    phone_number = fields.Integer(required=True)
    birthday = fields.DateTime(load_default=None, allow_none=True)


class MemberUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=40))
    email_address = fields.Email(validate=validate.Length(max=40))
    phone_number = fields.Integer()
    birthday = fields.DateTime(allow_none=True)
