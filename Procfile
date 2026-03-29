web: python3 scripts/auto_setup_render.py && gunicorn -c gunicorn_config.py --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --worker-class gevent web.app_professional:app
