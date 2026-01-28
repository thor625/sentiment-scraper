#!/usr/bin/env python3
import os
import time
from datetime import datetime, timedelta, timezone
import requests
import subprocess
import sys
from flask import Flask, request, jsonify, redirect, Response, g
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import func
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from rq.job import Job
from urllib.parse import quote as url_quote



from .db import db, migrate
from .models import StockQuote, SocialMention
from .pages import home_page_html, report_page_html
from .queue import get_queue
from .tasks import run_collectors_task




STOOQ_URL = "https://stooq.com/q/l/"
APP_START = time.time()
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["endpoint"])
REQUESTS_TOTAL = 0
ERRORS_TOTAL = 0

sentiment_analyzer = SentimentIntensityAnalyzer()


# Initialize once (cheap + thread-safe for this use case)

def run_collectors(symbol: str) -> dict:
    """
    Run both collectors using the same Python environment as the web app.
    Returns a small status dict for reporting.
    """
    quote_rc = subprocess.run([sys.executable, "-m", "scripts.fetch_quote", symbol]).returncode
    news_rc  = subprocess.run([sys.executable, "-m", "scripts.fetch_news_gdelt", symbol]).returncode
    return {"fetch_quote": quote_rc, "fetch_news_gdelt": news_rc}

def sentiment_label(avg_score: float | None) -> str:
    if avg_score is None:
        return "No data"
    if avg_score >= 0.2:
        return "Bullish 📈"
    if avg_score <= -0.2:
        return "Bearish 📉"
    return "Neutral ⚖️"

def score_sentiment(text: str) -> float:
    """
    Return VADER compound sentiment score in range [-1, 1]
    """
    if not text:
        return 0.0
    return sentiment_analyzer.polarity_scores(text)["compound"]

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
        "fetched_at": datetime.now(timezone.utc),
    }

FINNHUB_SEARCH_URL = "https://finnhub.io/api/v1/search"

def resolve_symbol(user_input: str) -> str:
    """
    Resolve user input (ticker or company name) to a canonical ticker symbol using Finnhub.
    Falls back to cleaned uppercase input if API key is missing or no match is found.
    """
    raw = (user_input or "").strip()
    if not raw:
        return ""

    # allow $AAPL style
    if raw.startswith("$"):
        raw = raw[1:].strip()

    # if user already gave a suffixed symbol (e.g., aapl.us), keep it
    # (we'll handle provider-specific formatting later)
    if "." in raw:
        return raw.upper()

    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return raw.upper()

    try:
        r = requests.get(
            FINNHUB_SEARCH_URL,
            params={"q": raw, "token": api_key},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("result", [])
        if results:
            # pick the top match
            return (results[0].get("symbol") or raw).upper()
    except Exception:
        pass

    return raw.upper()


def to_stooq_symbol(symbol: str) -> str:
    """
    Stooq commonly expects US tickers to have .US (e.g., AAPL.US).
    If user already provided a suffix like AAPL.US, keep it.
    """
    s = (symbol or "").strip().upper()
    if not s:
        return ""
    if "." in s:
        return s
    return s + ".US"

def create_app():
    app = Flask(__name__)

    project_root = os.path.dirname(os.path.dirname(__file__))

    # Local sqlite fallback
    db_path = os.path.join(project_root, "app.sqlite3")

    db_uri = os.getenv("DATABASE_URL")

    if db_uri:
        # Heroku uses deprecated postgres:// scheme
        if db_uri.startswith("postgres://"):
            db_uri = db_uri.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    else:
        # Local development only
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)


    @app.route("/collect", methods=["POST"])
    def collect():
        user_input = (request.form.get("symbol") or "").strip()

        # Resolve ONCE (keep suffix if provided)
        resolved_full = resolve_symbol(user_input)  # e.g. AMD, AMD.US, 000651.SZ
        if not resolved_full:
            return {"error": "Missing symbol"}, 400

        # Prefer async via Redis/RQ if configured; otherwise run inline
        try:
            q = get_queue()
            job = q.enqueue(run_collectors_task, resolved_full)
            return {"job_id": job.id, "symbol": resolved_full}, 202
        except Exception:
            # Redis not configured / not reachable -> run synchronously
            run_collectors_task(resolved_full)
            return {"job_id": None, "symbol": resolved_full, "status": "ran_inline"}, 200

    @app.route("/report")
    def report():
        user_input = (request.args.get("symbol") or "").strip()
        resolved_full = resolve_symbol(user_input)        # full (keeps suffix)
        canonical = resolved_full.split(".")[0]           # for SocialMention.symbol

        if not canonical:
            return '<p>Missing symbol. Try: <a href="/report?symbol=aapl">/report?symbol=aapl</a></p>'

        since = datetime.utcnow() - timedelta(days=1)

        resolved = canonical
        # news uses CANONICAL
        count = (
            db.session.query(func.count(SocialMention.id))
            .filter(SocialMention.platform == "news")
            .filter(SocialMention.symbol == canonical)
            .filter(SocialMention.created_at >= since)
            .scalar()
        ) or 0

        avg_sent = (
            db.session.query(func.avg(SocialMention.sentiment))
            .filter(SocialMention.platform == "news")
            .filter(SocialMention.symbol == canonical)
            .filter(SocialMention.created_at >= since)
            .scalar()
        )

        recent = (
            SocialMention.query
            .filter_by(platform="news", symbol=canonical)
            .filter(SocialMention.created_at >= since)
            .order_by(SocialMention.created_at.desc())
            .limit(25)
            .all()
        )

        # Sentiment buckets (VADER compound)
        pos = 0
        neu = 0
        neg = 0

        # Mentions per hour (last 24h)
        mentions_by_hour = {}  # key: "YYYY-mm-dd HH:00"

        # Quotes use STOOQ symbol (keep suffix if provided, else add .US)
        stooq_symbol = to_stooq_symbol(resolved_full)

        latest_quote = (
            StockQuote.query
            .filter_by(symbol=stooq_symbol)
            .order_by(StockQuote.fetched_at.desc())
            .first()
        )

        # Fallback for any older rows you may have saved as canonical (like "AMD")
        if not latest_quote:
            latest_quote = (
                StockQuote.query
                .filter(StockQuote.symbol.ilike(f"{canonical}%"))
                .order_by(StockQuote.fetched_at.desc())
                .first()
            )

        price_str = "NA"
        if latest_quote and latest_quote.close is not None:
            price_str = f"${latest_quote.close:.2f}"

        rows = ""
        for m in recent:
            sent_str = "NA" if m.sentiment is None else f"{m.sentiment:.3f}"
            headline = (m.text or "").replace("<", "&lt;").replace(">", "&gt;")  # basic HTML safety
            url = m.url or "#"
            # bucket sentiment
            s = m.sentiment
            if s is None:
                neu += 1
            elif s >= 0.2:
                pos += 1
            elif s <= -0.2:
                neg += 1
            else:
                neu += 1

            # hour key in UTC (created_at is stored as UTC-naive)
            hour_key = m.created_at.strftime("%Y-%m-%d %H:00")
            mentions_by_hour[hour_key] = mentions_by_hour.get(hour_key, 0) + 1

            rows += f"""
            <tr>
            <td>{m.created_at}</td>
            <td>{sent_str}</td>
            <td><a href="{url}" target="_blank" rel="noopener noreferrer">{headline}</a></td>
            </tr>
            """

        # Build mentions/hour table (sorted newest first)
        hour_rows = ""
        for hk in sorted(mentions_by_hour.keys(), reverse=True):
            hour_rows += f"<tr><td>{hk}</td><td>{mentions_by_hour[hk]}</td></tr>"

        avg_str = "NA" if avg_sent is None else f"{avg_sent:.3f}"

        sentiment_text = sentiment_label(avg_sent)

        return report_page_html(
            resolved=resolved,
            price_str=price_str,
            count=count,
            avg_str=avg_str,
            sentiment_text=sentiment_text,
            pos=pos,
            neu=neu,
            neg=neg,
            hour_rows=hour_rows,
            rows=rows,
        )

    @app.route("/")
    def main():
        return home_page_html()
    
    @app.route("/api/search")
    def api_search():
        q = (request.args.get("q") or "").strip()
        if not q:
            return jsonify([])

        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            return jsonify([])

        try:
            r = requests.get(
                FINNHUB_SEARCH_URL,
                params={"q": q, "token": api_key},
                timeout=10,
            )
            r.raise_for_status()
            results = r.json().get("result", [])[:8]  # limit suggestions

            # return only what the UI needs
            suggestions = [
                {
                    "symbol": item.get("symbol"),
                    "description": item.get("description"),
                    "type": item.get("type"),
                }
                for item in results
                if item.get("symbol")
            ]
            return jsonify(suggestions)
        except Exception:
            return jsonify([])

    @app.route("/track", methods=["POST"])
    def track():
        user_input = (request.form.get("symbol") or "").strip()

        # Resolve ONCE
        resolved_full = resolve_symbol(user_input)   # e.g. "AMD" or "AMD.US" or "000651.SZ"
        if not resolved_full:
            return "Missing symbol. Go back and enter one.", 400

        q = get_queue()

        # If Redis/RQ is configured, enqueue. Otherwise run inline.
        if q is not None:
            try:
                job = q.enqueue(run_collectors_task, resolved_full)
                return redirect(f"/report?symbol={url_quote(resolved_full)}&job_id={job.id}")
            except Exception:
                # Redis down / misconfigured -> fallback to synchronous
                pass

        # Fallback: run immediately (no job_id)
        run_collectors_task(resolved_full)
        return redirect(f"/report?symbol={url_quote(resolved_full)}")
        
    @app.before_request
    def before():
        g.start_time = time.time()

    @app.after_request
    def after(response):
        global REQUESTS_TOTAL, ERRORS_TOTAL

        REQUESTS_TOTAL += 1
        if response.status_code >= 500:
            ERRORS_TOTAL += 1

        # Prometheus client metrics
        try:
            endpoint = request.path
            REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
            dt = time.time() - g.start_time
            REQUEST_LATENCY.labels(endpoint).observe(dt)
        except Exception:
            pass

        return response
    
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    
    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "uptime_seconds": int(time.time() - APP_START),
            "db": "ok"
        }
    
        
    @app.route("/api/job/<job_id>")
    def api_job(job_id):
        try:
            q = get_queue()
        except Exception:
            q = None

        if q is None:
            return jsonify({"status": "unavailable", "reason": "rq/redis not configured"}), 503

        try:
            job = Job.fetch(job_id, connection=q.connection)
        except Exception:
            return jsonify({"status": "not_found"}), 404

        return jsonify({
            "id": job.id,
            "status": job.get_status(),   # queued/started/finished/failed
            "result": job.result,
            "exc_info": job.exc_info,
        })

    return app


app = create_app()