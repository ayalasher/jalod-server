try:
    from ..db import db
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db


class WelfareModel(db.Model):
    __tablename__ = "Welfare"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    amount_spent = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(
        db.Enum("Done", "Not Completed", name="welfare_status"),
        nullable=False,
    )
