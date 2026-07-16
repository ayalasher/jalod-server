try:
    from ..db import db
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
from werkzeug.security import check_password_hash, generate_password_hash

class memberModel(db.Model):
    __tablename__ = "Members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    email_address = db.Column(db.String(40), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    birthday = db.Column(db.DateTime, nullable=True)
    age_group = db.Column(db.String(20), nullable=True)
    total_contributions = db.Column(db.Numeric(10, 2), nullable=True)
    contributions_predated = db.Column(db.DateTime, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False, default="")
    contributions_tier = db.Column(db.Numeric(10, 2), nullable=True)
    contributions_debt = db.Column(db.Numeric(10, 2), nullable=True)
    loans_debt = db.Column(db.Numeric(10, 2), nullable=True)
    contributions_dated_at = db.Column(db.DateTime, nullable=True)
    ADMIN_ROLE = "admin"
    USER_ROLE = "user"
    role = db.Column(db.String(10), nullable=False, default=USER_ROLE, server_default=USER_ROLE)

    def is_admin(self) -> bool:
        return self.role == self.ADMIN_ROLE

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
   
