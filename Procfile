web: gunicorn src.app:app
worker: python worker.py
release: flask --app src.app:app db upgrade