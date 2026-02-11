# Sentiment Scraper

## Portfolio Snapshot
- Score: **8.8 / 10**
- Verdict: **Keep (flagship-ready)**
- Category: Full-stack data app

## Project Summary
Sentiment Scraper is a Flask application that collects market quote data and news headlines for a ticker, scores sentiment with VADER, stores results in a database, and serves a web report.

## What It Does
- Resolves ticker/company input using Finnhub search
- Fetches OHLCV quote data from Stooq
- Fetches recent news from GDELT and computes sentiment scores
- Stores quotes and mentions via SQLAlchemy models
- Shows a report with count, average sentiment, and sentiment buckets
- Exposes operational endpoints for health and Prometheus metrics
- Supports async collection with Redis/RQ and sync fallback

## Tech Stack
- Python, Flask, SQLAlchemy, Flask-Migrate
- VADER sentiment
- Redis + RQ
- Prometheus client
- PostgreSQL (prod) / SQLite (local)

## Repository Contents
- `src/app.py`: routes, report logic, metrics endpoints
- `src/models.py`: `StockQuote`, `SocialMention`
- `scripts/fetch_quote.py`: quote ingestion
- `scripts/fetch_news_gdelt.py`: news ingestion + sentiment
- `worker.py`: queue worker
- `tests/test_app.py`: basic unit tests

## Run Locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=src.app
flask run
```
Open `http://127.0.0.1:5000`.

## Why This Scores Well
- End-to-end engineering sample with app, jobs, data persistence, and observability
- Clear separation between web layer, task runners, and scripts
- Deploy-ready shape with `Procfile`, migrations, and worker process

## Improvement Priorities
- Expand test coverage across routes and collectors
- Add architecture diagram and API contract table
- Add Docker-based one-command startup
