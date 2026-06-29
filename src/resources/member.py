from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from models.member import memberModel

blp = Blueprint("members", __name__, description="Operations on members")


@blp.route("/members")
class Members(MethodView):
    @blp.response(200, description="Get all members")
    def get(self):
        """Get all members"""
        members = memberModel.query.all()
        return [
            {
                "id": member.id,
                "name": member.name,
                "email_address": member.email_address,
                "phone_number": member.phone_number,
                "birthday": member.birthday,
                "age_group": member.age_group,
            }
            for member in members
        ]


@blp.route("/members", methods=["POST"])
@blp.response(201, description="Register a member")
def register_member():
    """Register a new member"""
    data = request.get_json() or {}

    member = memberModel(
        name=data.get("name"),
        email_address=data.get("email_address"),
        phone_number=data.get("phone_number"),
        birthday=data.get("birthday"),
        age_group=data.get("age_group"),
    )

    db.session.add(member)
    db.session.commit()

    return {
        "id": member.id,
        "name": member.name,
        "email_address": member.email_address,
        "phone_number": member.phone_number,
        "birthday": member.birthday,
        "age_group": member.age_group,
    }, 201


@blp.route("/members/<int:member_id>")
@blp.response(200, description="Get a member by ID")
def get_member(member_id):
    """Get a member by ID"""
    member = memberModel.query.get(member_id)
    if not member:
        abort(404, message="Member not found")

    return {
        "id": member.id,
        "name": member.name,
        "email_address": member.email_address,
        "phone_number": member.phone_number,
        "birthday": member.birthday,
        "age_group": member.age_group,
    }


@blp.route("/members/<int:member_id>", methods=["PUT"])
@blp.response(200, description="Edit a member")
def edit_member(member_id):
    memberAttributes = ["name", "email_address", "phone_number", "birthday", "age_group"]
    """Edit a member by ID"""
    member = memberModel.query.get(member_id)
    if not member:
        abort(404, message="Member not found")

    data = request.get_json() or {}
    for field in memberAttributes:
        if field in data:
            setattr(member, field, data[field])

    db.session.commit()
    return {
        "id": member.id,
        "name": member.name,
        "email_address": member.email_address,
        "phone_number": member.phone_number,
        "birthday": member.birthday,
        "age_group": member.age_group,
    }


@blp.route("/members/<int:member_id>", methods=["DELETE"])
@blp.response(204, description="Delete a member")
def delete_member(member_id):
    """Delete a member by ID"""
    member = memberModel.query.get(member_id)
    if not member:
        abort(404, message="Member not found")

    return f"Member {member.name} deleted", 204