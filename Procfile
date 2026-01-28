web: gunicorn src.app:app
worker: rq worker -u $REDIS_URL sentiment-scraper
