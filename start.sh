#!/bin/bash

# Railway Startup Script
echo "🚀 Starting Professional Football Prediction System..."

# Set environment variables
export FLASK_APP=web/app_professional.py
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:/app"

# Create necessary directories
mkdir -p logs cache models/enterprise data

# Start the application
echo "📊 Loading models and data..."
python web/app_professional.py