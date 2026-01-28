#!/usr/bin/env python3
import sys
import requests
from datetime import datetime

from src.app import create_app, resolve_symbol, to_stooq_symbol
from src.db import db
from src.models import StockQuote

STOOQ_URL = "https://stooq.com/q/l/"


def fetch_quote(symbol: str):
    """
    Fetch OHLCV data from Stooq CSV endpoint.
    """
    params = {"s": symbol.lower(), "f": "sd2t2ohlcv", "h": "", "e": "csv"}
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
        "symbol": fields[0],            # e.g. AMD.US
        "open": to_float(fields[3]),
        "high": to_float(fields[4]),
        "low": to_float(fields[5]),
        "close": to_float(fields[6]),
        "volume": to_int(fields[7]),
        "fetched_at": datetime.utcnow(),
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fetch_quote <symbol-or-company>")
        sys.exit(1)

    user_input = sys.argv[1]

    # Resolve + convert to Stooq format so we store rows like AMD.US (not AMD)
    resolved = resolve_symbol(user_input)         # e.g. AMD
    stooq_symbol = to_stooq_symbol(resolved)      # e.g. AMD.US

    app = create_app()
    with app.app_context():
        quote_data = fetch_quote(stooq_symbol)

        quote = StockQuote(
            symbol=quote_data["symbol"],          # store AMD.US
            open=quote_data["open"],
            high=quote_data["high"],
            low=quote_data["low"],
            close=quote_data["close"],
            volume=quote_data["volume"],
            fetched_at=quote_data["fetched_at"],
        )

        db.session.add(quote)
        db.session.commit()

        print(f"Stored quote for {user_input} as {quote.symbol} at {quote.fetched_at} (close={quote.close})")


if __name__ == "__main__":
    main()