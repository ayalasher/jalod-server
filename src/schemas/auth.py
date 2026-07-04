from marshmallow import Schema, fields


class MemberSummarySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    email_address = fields.Str(dump_only=True)
    phone_number = fields.Int(dump_only=True)


class SignupRequestSchema(Schema):
    name = fields.Str(required=True, metadata={"description": "Member name used for login"})
    email_address = fields.Email(required=True, metadata={"description": "Member email address"})
    phone_number = fields.Int(required=True, metadata={"description": "Member phone number"})
    password = fields.Str(required=True, load_only=True, metadata={"description": "Plain-text password"})


class LoginRequestSchema(Schema):
    name = fields.Str(required=True, metadata={"description": "Member name"})
    password = fields.Str(required=True, load_only=True, metadata={"description": "Plain-text password"})


class AuthResponseSchema(Schema):
    message = fields.Str(dump_only=True)
    access_token = fields.Str(dump_only=True)
    member = fields.Nested(MemberSummarySchema, dump_only=True)