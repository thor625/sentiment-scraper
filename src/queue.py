# src/queue.py
import os
from redis import Redis
from rq import Queue

def get_redis_conn():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url)

def get_queue():
    return Queue("sentiment-scraper", connection=get_redis_conn(), default_timeout=300)