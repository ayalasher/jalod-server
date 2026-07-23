try:
    from ..db import db
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db


class ContributionModel(db.Model):
    """SQLAlchemy model for member contributions."""

    __tablename__ = "Contributions"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("Members.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(
        db.Enum("boma", "mpesa", "cash", "bank", name="contribution_type"),
        nullable=False,
    )

    member = db.relationship("memberModel", back_populates="contributions")
