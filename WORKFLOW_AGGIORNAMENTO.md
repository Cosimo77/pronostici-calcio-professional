# 🔄 Workflow Aggiornamento Dati Render

## 📌 Logica Corretta (Render FREE TIER)

### ❌ COSA NON FUNZIONA su Render FREE TIER

- Cron jobs automatici
- Background workers
- Script che scaricano dati esterni
- Processi che girano oltre 30 secondi

### ✅ COSA FUNZIONA

- Web server sempre online
- Ricaricamento dataset in memoria
- GitHub Actions trigger automatici
- Deploy automatico da GitHub

---

## 🔁 Workflow Completo

### 1. Aggiornamento Locale (MAC)

```bash
# Esegui su MAC per scaricare nuovi dati
python3 aggiornamento_dati_reali.py

# Oppure usa script rapido
python3 aggiorna_rapido.py

```

**Cosa fa:**

- Scarica ultimi risultati da football-data.co.uk
- Aggiorna `data/dataset_pulito.csv`
- Aggiorna `data/dataset_features.csv`

### 2. Commit e Push

```bash
git add data/dataset_pulito.csv data/dataset_features.csv
git commit -m "Update: dataset con partite fino a $(date +%d/%m/%Y)"
git push origin main

```


**Cosa fa:**

- Pusha nuovi dati su GitHub
- Render rileva commit e fa auto-deploy
- GitHub Actions rileva cambio file dataset

### 3. Reload Automatico su Render


**Trigger automatico via GitHub Actions:**

- File: `.github/workflows/reload_render.yml`
- Si attiva su: push di `data/dataset_*.csv`
- Chiama: `POST /api/automation/force_update`


**Endpoint su Render:**

```python
# web/app_professional.py
@app.route('/api/automation/force_update')
def api_force_update():
    # Ricarica dataset dal file deployato
    calculator.df_features = pd.read_csv('data/dataset_pulito.csv')
    return {'success': True, 'records': len(dataset)}

```

---

## 📊 Monitoraggio

### Check Manuale

```bash
# Verifica health
curl <<<<<https://pronostici-calcio-professional.onrender.com/api/health>>>>>

# Trigger manuale reload
curl -X POST <<<<<https://pronostici-calcio-professional.onrender.com/api/automation/force_update>>>>>

```

### GitHub <<<<<<https://github.com/Cosimo77/pronostici-calcio-professional/actions>>>>>>

1. Vai su: <<<<<https://github.com/Cosimo77/pronostici-calcio-professional/actions>>>>>
2. Workflow: "Reload Render Dataset"
3. Ultimo run dovrebbe essere verde ✅

---

## 🎯 Frequenza Aggiornamenti

### Raccomandato

- **Lunedì mattina**: Dopo weekend Serie A
- **Giovedì mattina**: Dopo turni infrasettimanali

### Comando Rapido

```bash
# Script tutto-in-uno
cd /Users/cosimomassaro/Desktop/pronostici_calcio
python3 aggiorna_rapido.py && \
git add data/*.csv && \
git commit -m "Update: nuove partite $(date +%d/%m)" && \
git push origin main

# GitHub Actions si occupa del resto automaticamente

```

---

## 🐛 Troubleshooting

### Problema: "Dati non aggiornati su Render"


**Soluzione:**

```bash
# 1. Verifica quante partite hai in locale
wc -l data/dataset_pulito.csv

# 2. Verifica quante su Render
curl <<<<<https://pronostici-calcio-professional.onrender.com/api/health>>>>> | grep database_records

# 3. Se diversi, trigger manuale reload
curl -X POST <<<<<https://pronostici-calcio-professional.onrender.com/api/automation/force_update>>>>>

```

### Problema: "GitHub Actions fallisce"


**Possibili cause:**

- Render in sleep (free tier dorme dopo 15min inattività)
- Endpoint non risponde → Render si sveglia automaticamente

**Soluzione:** Riprova workflow dopo 30 secondi

---

## 📝 Note Tecniche

### Perché non scarichiamo dati direttamente su Render?

1. **Timeout 30s**: Scraping richiede ~60s
2. **No background jobs**: Render FREE non supporta cron
3. **Affidabilità**: Locale è più controllabile

### Perché reload invece di update automatico?

1. **Render FREE limiti**: No cron, no workers
2. **Semplicità**: Git è la source of truth
3. **Tracciabilità**: Ogni update è un commit
4. **Rollback**: Facile tornare indietro con git

---

**Data:** 15 Gennaio 2026  
**Versione:** 3.0 (Hybrid Local+Cloud)
