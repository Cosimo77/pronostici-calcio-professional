#!/bin/bash
# Setup Environment Variables for Production Deploy

echo "🔐 Setup Environment Variables"
echo "================================"
echo ""

# Generate secure SECRET_KEY
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

echo "✅ SECRET_KEY generata: ${SECRET_KEY:0:20}..."
echo ""

# Create .env file
cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
PORT=5008

# Redis Cache (opzionale - se disponibile)
# REDIS_URL=redis://localhost:6379

# The Odds API (opzionale - per quote live)
# API_THE_ODDS=your_api_key_here

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ File .env creato"
echo ""
echo "📝 Contenuto .env:"
cat .env
echo ""
echo "⚠️  IMPORTANTE: Aggiungi .env al .gitignore!"
echo "⚠️  Per Render.com: Copia questi valori nelle Environment Variables"
echo ""
echo "✅ Setup completato!"
