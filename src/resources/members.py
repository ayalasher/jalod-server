from flask.views import MethodView
from flask_smorest import Blueprint, abort

try:
    from ..db import db
    from ..models.member import memberModel
    from ..schemas.member import BirthdaySchema, MemberCreateSchema, MemberSchema, MemberUpdateSchema
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
    from models.member import memberModel
    from schemas.member import BirthdaySchema, MemberCreateSchema, MemberSchema, MemberUpdateSchema

blp = Blueprint("members", __name__, description="Operations on members")


@blp.route("/members")
class Members(MethodView):
    @blp.response(200, schema=MemberSchema(many=True), description="Get all members")
    def get(self):
        """Get all members"""
        return memberModel.query.all()

    @blp.arguments(MemberCreateSchema, location="json")
    @blp.response(201, schema=MemberSchema, description="Register a member")
    def post(self, payload):
        """Register a new member"""
        member = MemberSchema().load(payload, session=db.session)

        db.session.add(member)
        db.session.commit()

        return member, 201


@blp.route("/members/birthdays")
class MemberBirthdays(MethodView):
    @blp.response(200, schema=BirthdaySchema(many=True), description="Get all member birthdays")
    def get(self):
        """Get all member birthdays"""
        birthdays = (
            memberModel.query.filter(memberModel.birthday.isnot(None))
            .order_by(memberModel.birthday.asc())
            .all()
        )

        return [
            {
                "id": member.id,
                "name": member.name,
                "birthday": member.birthday,
            }
            for member in birthdays
        ]


@blp.route("/members/<int:member_id>")
class Member(MethodView):
    @blp.response(200, schema=MemberSchema, description="Get a member by ID")
    def get(self, member_id):
        """Get a member by ID"""
        member = memberModel.query.get(member_id)
        if not member:
            abort(404, message="Member not found")

        return member

    @blp.arguments(MemberUpdateSchema, location="json")
    @blp.response(200, schema=MemberSchema, description="Edit a member")
    def put(self, payload, member_id):
        """Edit a member by ID"""
        member = memberModel.query.get(member_id)
        if not member:
            abort(404, message="Member not found")

        member = MemberSchema().load(payload, instance=member, partial=True, session=db.session)
        db.session.commit()
        return member

    @blp.response(204, description="Delete a member")
    def delete(self, member_id):
        """Delete a member by ID"""
        member = memberModel.query.get(member_id)
        if not member:
            abort(404, message="Member not found")

        db.session.delete(member)
        db.session.commit()

        return f"Member deleted {member.name}", 204