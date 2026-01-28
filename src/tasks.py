# src/tasks.py
import subprocess
import sys

def run_collectors_task(symbol: str) -> dict:
    quote_rc = subprocess.run([sys.executable, "-m", "scripts.fetch_quote", symbol]).returncode
    news_rc  = subprocess.run([sys.executable, "-m", "scripts.fetch_news_gdelt", symbol]).returncode
    return {"fetch_quote": quote_rc, "fetch_news_gdelt": news_rc}