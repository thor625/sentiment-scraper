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

class SocialMention(db.Model):
    __tablename__ = "social_mentions"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)      # "reddit" or "x"
    source = db.Column(db.String(120), nullable=True)        # subreddit name or account name
    symbol = db.Column(db.String(32), nullable=False)         # canonical ticker (e.g., AAPL)
    created_at = db.Column(db.DateTime, nullable=False)       # post/comment time (UTC)
    fetched_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=True)

    sentiment = db.Column(db.Float, nullable=True)           # VADER compound [-1, 1]