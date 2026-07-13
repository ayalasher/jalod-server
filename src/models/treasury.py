try:
    from ..db import db
except ImportError:  # pragma: no cover - allows running from src directory
    from db import db


class TreasuryModel(db.Model):
    __tablename__ = "Treasury"

    id = db.Column(db.Integer, primary_key=True)
    current_balance = db.Column(db.Numeric(12, 2), nullable=True)
    money_in_this_year = db.Column(db.Numeric(12, 2), nullable=True)
    money_out_this_year = db.Column(db.Numeric(12, 2), nullable=True)
    current_balance_date = db.Column(db.DateTime, nullable=True)
    boma_yangu = db.Column(db.Numeric(12, 2), nullable=True)
    market_fund = db.Column(db.Numeric(12, 2), nullable=True)
    government_bonds = db.Column(db.Numeric(12, 2), nullable=True)
    cryptocurrency = db.Column(db.Numeric(12, 2), nullable=True)
