#!/bin/bash

echo "🚀 Configurazione per Deploy Online"
echo "=================================="

# Crea file requirements.txt automaticamente
echo "📦 Creazione requirements.txt..."
pip3 freeze > requirements.txt

# Aggiungi dipendenze essenziali se mancanti
echo "Flask>=2.0.0" >> requirements.txt
echo "pandas>=1.5.0" >> requirements.txt
echo "numpy>=1.21.0" >> requirements.txt
echo "scikit-learn>=1.1.0" >> requirements.txt
echo "flask-limiter>=3.0.0" >> requirements.txt
echo "flask-talisman>=1.0.0" >> requirements.txt
echo "structlog>=22.0.0" >> requirements.txt

# Rimuovi duplicati
sort requirements.txt | uniq > requirements_clean.txt
mv requirements_clean.txt requirements.txt

echo "✅ requirements.txt creato"

# Crea app.json per Heroku
cat > app.json << EOF
{
  "name": "Pronostici Calcio Professional",
  "description": "Sistema professionale di pronostici calcio con ML",
  "repository": "https://github.com/your-username/pronostici_calcio",
  "logo": "https://cdn.iconscout.com/icon/free/png-256/football-1-152755.png",
  "keywords": ["football", "soccer", "predictions", "ml", "flask"],
  "env": {
    "FLASK_ENV": {
      "description": "Flask environment",
      "value": "production"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "free"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
EOF

echo "✅ app.json creato per Heroku"

# Crea .env per configurazione locale
cat > .env << EOF
# Configurazione Locale
FLASK_ENV=development
PORT=5008

# Configurazione Produzione (impostare su piattaforma di deploy)
# FLASK_ENV=production
# PORT=\$PORT (impostato automaticamente)
EOF

echo "✅ .env creato"

# Crea deploy.md con istruzioni
cat > DEPLOY.md << EOF
# 🌐 Deploy Online - Guida Completa

## 1. 🚀 Heroku (Gratis)

### Setup iniziale:
\`\`\`bash
# Installa Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Crea app
heroku create nome-tua-app-pronostici

# Deploy
git add .
git commit -m "Deploy professionale"
git push heroku main
\`\`\`

### URL finale:
\`https://nome-tua-app-pronostici.herokuapp.com\`

## 2. 🚄 Railway (Moderno)

### Setup:
1. Vai su railway.app
2. Connetti GitHub repo
3. Deploy automatico!

### URL finale:
\`https://pronostici-calcio-production.up.railway.app\`

## 3. 🌊 Vercel (Semplice)

### Setup:
\`\`\`bash
npm i -g vercel
vercel
\`\`\`

## 4. 📱 Render (Affidabile)

1. Vai su render.com
2. Connetti repo GitHub
3. Seleziona "Web Service"
4. Deploy automatico!

## ⚙️ Configurazioni Necessarie

### Variabili d'ambiente:
- \`FLASK_ENV=production\`
- \`PORT=\$PORT\` (automatico)

### File necessari:
- ✅ Procfile
- ✅ requirements.txt  
- ✅ runtime.txt
- ✅ app.json

## 🔧 Troubleshooting

### Errore memoria:
- Riduci dataset se necessario
- Usa piano a pagamento

### Errore SSL:
- Controlla configurazione Talisman
- Verifica CSP headers

### Performance:
- Abilita caching
- Ottimizza calcoli ML
EOF

echo "✅ DEPLOY.md creato con istruzioni complete"

echo ""
echo "🎉 SETUP DEPLOY COMPLETATO!"
echo "=================================="
echo "Files creati:"
echo "- Procfile (Heroku/Railway)"
echo "- runtime.txt (Python version)"
echo "- requirements.txt (Dipendenze)"
echo "- app.json (Configurazione Heroku)"
echo "- .env (Variabili locali)"
echo "- DEPLOY.md (Istruzioni complete)"
echo ""
echo "🚀 Prossimi passi:"
echo "1. Scegli piattaforma (Heroku/Railway/Vercel/Render)"
echo "2. Segui istruzioni in DEPLOY.md"
echo "3. Goditi la tua app online! 🌐"