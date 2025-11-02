# 🚀 Guida Deploy Render

Guida completa per il deployment su Render.com con auto-deploy da GitHub.

## 📋 Prerequisiti

- Account GitHub (repository pubblico o privato)
- Account Render.com (gratuito)
- Repository con codice aggiornato

## 🎯 Setup Iniziale

### 1. Preparazione Repository

```bash
# Assicurati che tutti i file siano committati
git status
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Files Richiesti

#### `requirements.txt`

```text
Flask==3.1.0
pandas==2.1.0
numpy==1.25.2
scikit-learn==1.3.0
flask-talisman==1.1.0
flask-limiter==3.5.0
structlog==23.1.0
gunicorn==21.2.0
gevent==23.9.1
```

#### `Procfile`

```text
web: gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:$PORT web.app_professional:app --timeout 120 --log-file=-
```

#### `runtime.txt`

```text
python-3.11.0
```

## 🌐 Creazione Web Service

### Step 1: Nuovo Web Service

1. Vai su [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connetti GitHub repository
4. Autorizza Render ad accedere al repo

### Step 2: Configurazione Service

| Campo | Valore |
|-------|--------|
| **Name** | `pronostici-calcio-professional` |
| **Environment** | `Python 3` |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | (usa Procfile automaticamente) |

### Step 3: Environment Variables

Aggiungi se necessario:

```text
PYTHON_VERSION=3.11.0
PORT=5008
FLASK_ENV=production
```

### Step 4: Piano Gratuito

- Seleziona **"Free"**
- ⚠️ Limiti free tier:
  - 512MB RAM
  - Sleep dopo 15min inattività
  - 750 ore/mese

### Step 5: Deploy

Click **"Create Web Service"**

Render inizierà automaticamente:

1. Clone repository
2. Build (pip install)
3. Start (Procfile command)

## 📊 Monitoring Deploy

### Logs Real-Time

Nel dashboard Render:

- Tab **"Logs"** → vedi output live
- Cerca `Sistema inizializzato` per conferma

### Status Deploy

```text
✅ Deploy live
⏸️ Sleeping (inattività)
🔄 Building
❌ Failed
```

### Health Check

```bash
# Via curl
curl https://pronostici-calcio-professional.onrender.com/api/health

# Risposta attesa
{
  "status": "healthy",
  "database_records": 1894,
  "squadre_caricate": 20
}
```

## 🔄 Auto-Deploy da GitHub

### Configurazione

Render monitora automaticamente il branch `main`.

Ogni push attiva deploy automatico:

```bash
# Modifica codice
git add .
git commit -m "Update feature"
git push origin main

# Render auto-deploya (2-3 minuti)
```

### Verifica Auto-Deploy

1. Push su GitHub
2. Vai su dashboard Render
3. Vedi "Building..." in **Events**
4. Attendi "Deploy live"

## 🐛 Troubleshooting

### Build Failed

#### Errore: Requirements Install

```bash
# Verifica requirements.txt localmente
pip install -r requirements.txt

# Verifica versioni compatibili
pip list
```

#### Errore: Python Version

```bash
# Verifica runtime.txt
cat runtime.txt
# Deve essere: python-3.11.0

# Versioni supportate: https://render.com/docs/python-version
```

### Deploy Failed

#### Errore: Application Crash

```bash
# Check logs Render per traceback
# Cerca "ERROR" o "Exception"

# Testa localmente
python -m web.app_professional
```

#### Errore: Port Binding

```python
# Assicurati di usare $PORT environment variable
port = int(os.environ.get('PORT', 5008))
app.run(host='0.0.0.0', port=port)
```

### Service Sleeping

⚠️ Free tier dorme dopo 15min inattività

```bash
# Ping per risvegliare (50sec cold start)
curl https://pronostici-calcio-professional.onrender.com/

# Considera ping periodico:
# - UptimeRobot (gratuito)
# - Cron job ogni 10min
```

### 502 Bad Gateway

```bash
# Cause comuni:
# 1. App non risponde su $PORT
# 2. Timeout gunicorn (aumenta in Procfile)
# 3. OOM (Out of Memory - 512MB limite)

# Verifica worker config
gunicorn --workers 2  # Riduci worker se OOM
```

## 🔧 Ottimizzazioni

### Performance

```python
# Procfile ottimizzato
web: gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:$PORT web.app_professional:app --timeout 180 --keep-alive 5 --log-file=-
```

### Memoria

```python
# Riduci workers se necessario
--workers 2  # invece di 4

# Limita cache
--max-requests 1000
--max-requests-jitter 50
```

### Cold Start

```python
# Riduci dipendenze
# Lazy loading modelli
# Pre-warm cache essenziale
```

## 📈 Monitoring Produzione

### Metrics Dashboard

Render fornisce:

- CPU usage
- Memory usage
- Response time
- Error rate

### Custom Monitoring

```python
# /api/health endpoint
@app.route('/api/health')
def health():
    return {
        'status': 'healthy',
        'uptime': get_uptime(),
        'memory': get_memory_usage()
    }
```

### Logs

```bash
# Download logs
render logs --tail 1000

# Stream logs
render logs --follow
```

## 🔐 Sicurezza

### HTTPS

✅ Automatico con Render (certificato SSL gratuito)

### Environment Secrets

```python
# Mai committare secrets in codice
# Usa Environment Variables in Render dashboard

# Esempio
API_KEY = os.environ.get('API_KEY')
```

### Rate Limiting

```python
# Implementato in app_professional.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["100 per hour"]
)
```

## 🎯 Best Practices

### Pre-Deploy Checklist

- [ ] Test localmente
- [ ] Requirements.txt aggiornato
- [ ] Procfile corretto
- [ ] Environment variables settate
- [ ] Health endpoint funzionante
- [ ] Logs configurati

### Post-Deploy Checklist

- [ ] Health check OK
- [ ] Dashboard carica
- [ ] API rispondono
- [ ] Logs puliti (no ERROR)
- [ ] Performance accettabili

### Maintenance

```bash
# Deploy manuale forzato
git commit --allow-empty -m "Force rebuild"
git push origin main

# Rollback a commit precedente
git revert HEAD
git push origin main
```

## 🆘 Support

### Documentazione Ufficiale

- [Render Python Docs](https://render.com/docs/deploy-flask)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Flask Production](https://flask.palletsprojects.com/en/3.0.x/deploying/)

### Render Support

- Dashboard → Support
- Community forum
- Email: <support@render.com>

---

Guida Deploy v1.0 - Aggiornato il 2 Novembre 2025
