#!/usr/bin/env python3
import os
from datetime import datetime

import requests
from flask import Flask, request

from .db import db, migrate
from .models import StockQuote


STOOQ_URL = "https://stooq.com/q/l/"


def fetch_quote(symbol: str):
    params = {
        "s": symbol.lower(),
        "f": "sd2t2ohlcv",
        "h": "",
        "e": "csv",
    }
    response = requests.get(STOOQ_URL, params=params, timeout=10)
    response.raise_for_status()

    lines = response.text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("Unexpected response format from quote source")

    data = lines[1]
    fields = data.split(",")

    # fields: Symbol,Date,Time,Open,High,Low,Close,Volume
    def is_missing(x: str) -> bool:
        return x is None or x.strip() in {"", "N/A", "N/D", "NA", "ND"}

    def to_float(x):
        return None if is_missing(x) else float(x)

    def to_int(x):
        return None if is_missing(x) else int(float(x))

    return {
        "symbol": fields[0],
        "open": to_float(fields[3]),
        "high": to_float(fields[4]),
        "low": to_float(fields[5]),
        "close": to_float(fields[6]),
        "volume": to_int(fields[7]),
        "fetched_at": datetime.utcnow(),
    }


def create_app():
    app = Flask(__name__)

    # Local default: SQLite file in project root
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.sqlite3")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def main():
        return """
        <h2>Stock Quote Fetcher</h2>
        <form action="/track" method="POST">
            <label>Symbol (example: aapl.us)</label><br/>
            <input name="symbol" />
            <input type="submit" value="Fetch + Store" />
        </form>
        """

    @app.route("/track", methods=["POST"])
    def track():
        symbol = (request.form.get("symbol", "") or "").strip()
        if not symbol:
            return "Missing symbol. Go back and enter one.", 400

        # Fetch external data
        quote_data = fetch_quote(symbol)

        # Store in DB
        quote = StockQuote(
            symbol=quote_data["symbol"],
            open=quote_data["open"],
            high=quote_data["high"],
            low=quote_data["low"],
            close=quote_data["close"],
            volume=quote_data["volume"],
            fetched_at=quote_data["fetched_at"],
        )
        db.session.add(quote)
        db.session.commit()

        # Display recent entries for that symbol
        recent = (
            StockQuote.query.filter_by(symbol=quote_data["symbol"])
            .order_by(StockQuote.fetched_at.desc())
            .limit(10)
            .all()
        )

        rows_html = ""
        for r in recent:
            rows_html += f"""
            <tr>
              <td>{r.symbol}</td>
              <td>{r.open}</td>
              <td>{r.high}</td>
              <td>{r.low}</td>
              <td>{r.close}</td>
              <td>{r.volume}</td>
              <td>{r.fetched_at}</td>
            </tr>
            """

        return f"""
        <h3>Stored latest quote for {quote_data["symbol"]}</h3>
        <p>Close: {quote_data["close"]} | Volume: {quote_data["volume"]} | Fetched at: {quote_data["fetched_at"]}</p>

        <h4>Recent stored quotes (up to 10)</h4>
        <table border="1" cellpadding="6">
          <tr>
            <th>Symbol</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th><th>Fetched At (UTC)</th>
          </tr>
          {rows_html}
        </table>

        <p><a href="/">Back</a></p>
        """

    return app


app = create_app()