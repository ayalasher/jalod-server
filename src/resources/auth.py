from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort

from models.member import memberModel
from db import db
from schemas.auth import AuthResponseSchema, LoginRequestSchema, SignupRequestSchema


blp = Blueprint("auth", __name__, description="Authentication operations")


def _parse_phone_number(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        stripped_value = value.strip()
        if not stripped_value:
            return None
        if stripped_value.isdigit():
            return int(stripped_value)

    abort(400, message="phone_number must be a valid number")


@blp.route("/auth/signup")
class SignUp(MethodView):
    @blp.arguments(SignupRequestSchema)
    @blp.response(201, schema=AuthResponseSchema, description="Create a new member account")
    def post(self, payload):
        name = payload["name"].strip()
        email_address = payload["email_address"].strip()
        phone_number = _parse_phone_number(payload["phone_number"])
        password = payload["password"]

        if memberModel.query.filter_by(name=name).first():
            abort(409, message="Member with this name already exists")

        if memberModel.query.filter_by(email_address=email_address).first():
            abort(409, message="Member with this email already exists")

        member = memberModel(
            name=name,
            email_address=email_address,
            phone_number=phone_number,
        )
        member.set_password(password)

        db.session.add(member)
        db.session.commit()

        token = create_access_token(identity=str(member.id), additional_claims={"name": member.name})
        return {
            "message": "Signup successful",
            "access_token": token,
            "member": {
                "id": member.id,
                "name": member.name,
                "email_address": member.email_address,
                "phone_number": member.phone_number,
            },
        }, 201


@blp.route("/auth/login")
class Login(MethodView):
    @blp.arguments(LoginRequestSchema)
    @blp.response(200, schema=AuthResponseSchema, description="Login with name and password")
    def post(self, payload):
        name = payload["name"].strip()
        password = payload["password"]

        member = memberModel.query.filter_by(name=name).first()
        if not member or not member.check_password(password):
            abort(401, message="Invalid credentials")

        token = create_access_token(identity=str(member.id), additional_claims={"name": member.name})
        return {
            "message": "Login successful",
            "access_token": token,
            "member": {
                "id": member.id,
                "name": member.name,
                "email_address": member.email_address,
                "phone_number": member.phone_number,
            },
        }, 200