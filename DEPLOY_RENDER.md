# 🚀 Deploy su Render - Guida Completa

## 📋 Prerequisiti
- Account GitHub con repository `pronostici-calcio-professional`
- Account Render gratuito (https://render.com)
- Codice già committato con configurazioni aggiornate

## 🔧 Configurazione Automatica

### 1. Connetti Repository GitHub
1. Login su **Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. **Connect a repository** → Autorizza GitHub
4. Seleziona repository: `Cosimo77/pronostici-calcio-professional`

### 2. Configurazione Web Service

#### Settings Base:
```yaml
Name: pronostici-calcio-pro
Region: Frankfurt (EU Central)
Branch: main
Runtime: Docker
Dockerfile Path: ./Dockerfile
Docker Context: .
```

#### Settings Avanzate:
```yaml
Instance Type: Free
Health Check Path: /api/health
Auto-Deploy: Yes
```

#### Variabili Ambiente:
```bash
FLASK_ENV=production
PORT=5008  # Render assegna dinamicamente
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### 3. Deploy Automatico
1. Click **"Create Web Service"**
2. Render inizia build Docker automatico
3. Attendi 5-10 minuti per primo deploy
4. URL generato: `https://pronostici-calcio-pro.onrender.com`

## 🔄 Aggiornamenti Automatici (Cron Job)

### Setup Cron Service:
1. Dashboard Render → **"New +"** → **"Cron Job"**
2. Connetti stesso repository
3. Configurazione:

```yaml
Name: aggiorna-dati-quotidiano
Region: Frankfurt
Runtime: Docker
Schedule: 0 2 * * *  # Ogni giorno 2:00 AM
Command: python3 scripts/aggiorna_quotidiano.py
```

## 📊 Monitoring & Health Check

### Endpoints Disponibili:
```bash
# Health Check (Render monitora automaticamente)
GET https://pronostici-calcio-pro.onrender.com/api/health

# Status Sistema
GET https://pronostici-calcio-pro.onrender.com/api/status

# Dashboard Monitoring
GET https://pronostici-calcio-pro.onrender.com/monitoring

# Automazione Status
GET https://pronostici-calcio-pro.onrender.com/automation
```

### Logs in Tempo Reale:
```bash
# Dal dashboard Render
Dashboard → Service → Logs (tab)

# Ultimi 100 log
Dashboard → Service → Shell → tail -100 logs/automation_master.log
```

## 🎯 API Enterprise Endpoints

### Predizione Singola Partita:
```bash
curl -X POST https://pronostici-calcio-pro.onrender.com/api/predict_enterprise \
  -H "Content-Type: application/json" \
  -d '{
    "casa": "Inter",
    "trasferta": "Milan",
    "usa_cache": true
  }'
```

### Predizioni Giornata:
```bash
curl https://pronostici-calcio-pro.onrender.com/api/predictions/today
```

## ⚠️ Limitazioni Piano Free Render

### Risorse Disponibili:
- **RAM**: 512 MB
- **CPU**: 0.1 vCPU condivisa
- **Disco**: 1 GB effimero (restart = perdita dati)
- **Sleeping**: Dopo 15 min inattività (wake-up 30-60s)
- **Build**: 500 minuti/mese
- **Bandwidth**: Illimitata

### Ottimizzazioni per Free Tier:
```python
# Già implementate nel codice:
- Cache in-memory per predizioni (no database)
- Workers ridotti: 2 invece di 4
- Timeout aumentato: 120s per wake-up
- Modelli pre-trained inclusi (no training online)
```

## 🔐 Sicurezza & Best Practices

### Headers Sicurezza (già configurati):
```python
# Flask-Talisman attivo in app_professional.py
- HTTPS obbligatorio (Render fornisce certificato SSL)
- Content-Security-Policy
- X-Frame-Options: DENY
- Strict-Transport-Security
```

### Rate Limiting (già attivo):
```python
# Flask-Limiter configurato
/api/predict_enterprise: 60 richieste/ora per IP
/api/*: 1000 richieste/giorno
```

## 📈 Upgrade a Piano Paid (Opzionale)

### Starter Plan ($7/mese):
- **RAM**: 512 MB garantita
- **No sleeping**: Sempre attivo
- **Build**: Illimitati
- **Custom domain**: Supporto

### Standard Plan ($25/mese):
- **RAM**: 2 GB
- **Auto-scaling**
- **Database incluso**: PostgreSQL
- **Priority support**

## 🚨 Troubleshooting

### Deploy Fallito:
```bash
# Check logs durante build
Dashboard → Service → Logs → Filter "ERROR"

# Errori comuni:
1. requirements.txt incompatibilità → Verifica versioni
2. Dockerfile sintassi → Valida localmente: docker build -t test .
3. Porta errata → Usa $PORT variabile Render
```

### App Non Risponde:
```bash
# 1. Verifica sleeping
Dashboard → Service → Metrics → Check "Requests"

# 2. Restart manuale
Dashboard → Service → Manual Deploy → "Deploy latest commit"

# 3. Check health endpoint
curl https://pronostici-calcio-pro.onrender.com/api/health
```

### Performance Lente:
```bash
# Piano free ha cold start dopo 15 min
Soluzione: Upgrade a Starter per eliminare sleeping

# Ottimizzazione cache
Dashboard → Service → Environment → CACHE_SIZE=1000
```

## 🔄 CI/CD Automatico

### Workflow GitHub → Render:
```yaml
# Già configurato automaticamente
1. Push codice su main
2. Render rileva commit
3. Build Docker automatico
4. Deploy nuovo container
5. Health check automatico
6. Rollback se fallisce
```

### Rollback Manuale:
```bash
Dashboard → Service → Deploys → 
Select previous deploy → "Rollback to this version"
```

## 📞 Support & Links

- **Render Docs**: https://render.com/docs
- **Status Page**: https://status.render.com
- **Community**: https://community.render.com
- **Repository**: https://github.com/Cosimo77/pronostici-calcio-professional

---

## ✅ Checklist Deploy

- [ ] Repository GitHub pubblico/privato accessibile
- [ ] `render.yaml` committato
- [ ] `Dockerfile` con CMD usando $PORT
- [ ] `requirements.txt` con gevent
- [ ] `Procfile` aggiornato
- [ ] Account Render creato
- [ ] Repository connesso a Render
- [ ] Web Service configurato
- [ ] Variabili ambiente impostate
- [ ] Deploy completato con successo
- [ ] Health check passa (verde)
- [ ] Test API endpoint funzionanti
- [ ] (Opzionale) Cron job configurato
- [ ] (Opzionale) Custom domain configurato

**Sistema pronto per produzione su Render! 🎉**
