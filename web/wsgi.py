#!/usr/bin/env python3
"""
Gunicorn WSGI entry point per Railway deployment
"""

import os
import sys

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa l'app Flask
from app_professional import app

if __name__ == "__main__":
    # Per testing locale
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))