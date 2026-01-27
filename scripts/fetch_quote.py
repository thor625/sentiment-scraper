#!/usr/bin/env python3
import sys
import requests
from datetime import datetime

from src.app import create_app
from src.db import db
from src.models import StockQuote


STOOQ_URL = "https://stooq.com/q/l/"


def fetch_quote(symbol: str):
    """
    Fetch OHLCV data from Stooq CSV endpoint.
    """
    params = {
        "s": symbol.lower(),
        "f": "sd2t2ohlcv",
        "h": "",
        "e": "csv",
    }

    response = requests.get(STOOQ_URL, params=params, timeout=10)
    response.raise_for_status()

    lines = response.text.strip().splitlines()
    header, data = lines[0], lines[1]
    fields = data.split(",")

    return {
        "symbol": fields[0],
        "open": float(fields[3]) if fields[3] != "N/A" else None,
        "high": float(fields[4]) if fields[4] != "N/A" else None,
        "low": float(fields[5]) if fields[5] != "N/A" else None,
        "close": float(fields[6]) if fields[6] != "N/A" else None,
        "volume": int(fields[7]) if fields[7] != "N/A" else None,
        "fetched_at": datetime.utcnow(),
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/fetch_quote.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]

    app = create_app()
    with app.app_context():
        quote_data = fetch_quote(symbol)

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

        print(f"Stored quote for {symbol} at {quote.fetched_at}")


if __name__ == "__main__":
    main()