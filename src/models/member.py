try:
    from ..db import db
    from .contribution import ContributionModel
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db
    from contribution import ContributionModel
from werkzeug.security import check_password_hash, generate_password_hash

class memberModel(db.Model):
    """SQLAlchemy model for application members.

    This model stores public member fields (name, email, birthday) as well
    as authentication and contribution-related fields (password_hash, role,
    contributions_*). The class exposes a small helper `is_admin()` used by
    resource-level authorization checks.
    """
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
    contributions = db.relationship(
        "ContributionModel",
        back_populates="member",
        cascade="all, delete-orphan",
    )

    # Simple role constants to avoid magic strings throughout the codebase.
    ADMIN_ROLE = "admin"
    USER_ROLE = "user"
    role = db.Column(db.String(10), nullable=False, default=USER_ROLE, server_default=USER_ROLE)

    def is_admin(self) -> bool:
        """Return True if this member has the admin role."""
        return self.role == self.ADMIN_ROLE

    def set_password(self, password: str) -> None:
        """Hash and store the provided plain-text password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)
   
