# src/queue.py
import os
import redis
from rq import Queue

QUEUE_NAME = os.getenv("RQ_QUEUE_NAME", "sentiment-scraper")

def get_redis_url() -> str | None:
    # Heroku Redis normally sets REDIS_URL.
    # Locally you can set it too, or fall back to localhost only when not on Heroku.
    url = os.getenv("REDIS_URL")
    if url:
        return url

    # If running on Heroku and REDIS_URL is missing, DO NOT fall back to localhost.
    if os.getenv("DYNO"):
        return None

    # local dev default
    return "redis://localhost:6379/0"


def get_redis_conn():
    url = get_redis_url()
    if not url:
        return None

    # Some hosted redis providers require TLS; this handles rediss:// URLs too.
    # ssl_cert_reqs=None avoids cert issues in some setups.
    return redis.from_url(url, ssl_cert_reqs=None)


def get_queue() -> Queue | None:
    conn = get_redis_conn()
    if not conn:
        return None
    return Queue(QUEUE_NAME, connection=conn, default_timeout=300)