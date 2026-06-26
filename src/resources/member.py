# from flask.views import MethodView
from flask_smorest import Blueprint

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