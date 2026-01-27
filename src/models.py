from datetime import datetime
from .db import db

class StockQuote(db.Model):
    __tablename__ = "stock_quotes"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), nullable=False, index=True)
    fetched_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Basic OHLCV fields
    open = db.Column(db.Float, nullable=True)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    close = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Integer, nullable=True)

    source = db.Column(db.String(64), nullable=False, default="stooq")