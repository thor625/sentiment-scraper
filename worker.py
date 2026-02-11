# worker.py
import os
import redis
from rq import Worker, Queue

# Keep compatibility with both env names used in this repo.
queue_name = os.getenv("RQ_QUEUE_NAME") or os.getenv("RQ_QUEUE") or "sentiment-scraper"
listen = [queue_name]

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work(with_scheduler=True)
