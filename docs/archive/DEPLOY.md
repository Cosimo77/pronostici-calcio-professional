# 🌐 Deploy Online - Guida Completa

## 1. 🚀 Heroku (Gratis)

### Setup iniziale:
```bash
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
```

### URL finale:
`https://nome-tua-app-pronostici.herokuapp.com`

## 2. 🚄 Railway (Moderno)

### Setup:
1. Vai su railway.app
2. Connetti GitHub repo
3. Deploy automatico!

### URL finale:
`https://pronostici-calcio-production.up.railway.app`

## 3. 🌊 Vercel (Semplice)

### Setup:
```bash
npm i -g vercel
vercel
```

## 4. 📱 Render (Affidabile)

1. Vai su render.com
2. Connetti repo GitHub
3. Seleziona "Web Service"
4. Deploy automatico!

## ⚙️ Configurazioni Necessarie

### Variabili d'ambiente:
- `FLASK_ENV=production`
- `PORT=$PORT` (automatico)

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
