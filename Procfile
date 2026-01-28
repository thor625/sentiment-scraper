web: gunicorn src.app:app
worker: python worker.py
release: python -m flask --app src.app:app db upgrade