# src/tasks.py
import subprocess
import sys


def run_collectors_task(symbol: str) -> dict:
    """Run quote and news collection scripts for a single symbol."""
    quote_rc = subprocess.run([sys.executable, "-m", "scripts.fetch_quote", symbol]).returncode
    news_rc = subprocess.run([sys.executable, "-m", "scripts.fetch_news_gdelt", symbol]).returncode
    return {"fetch_quote": quote_rc, "fetch_news_gdelt": news_rc}
