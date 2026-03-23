# 🔄 Sistema Auto-Aggiornamento Dataset

## ✅ PROBLEMA RISOLTO

Dataset non si aggiornava automaticamente → **ora aggiornato programmaticamente con 1 comando**

## 🚀 Uso Rapido

### Aggiornamento Manuale (Locale)

```bash
# Aggiorna dati + rigenera dataset
python3 scripts/update_dataset_and_reload.py

# Con reload automatico app Render
python3 scripts/update_dataset_and_reload.py --reload-render
```

### Aggiornamento Automatico (Cron Job)

Aggiungi a crontab per esecuzione giornaliera:

```bash
# Edit cron jobs
crontab -e

# Aggiungi riga (ogni giorno alle 6:00 AM):
0 6 * * * cd /Users/cosimomassaro/Desktop/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render >> logs/update_dataset.log 2>&1
```

**Altre schedules utili:**

```bash
# Ogni 12 ore (6:00 e 18:00)
0 6,18 * * * cd /path/to/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render

# Ogni lunedì mattina alle 5:00
0 5 * * 1 cd /path/to/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render

# Ogni giorno alle 7:00, 13:00, 19:00
0 7,13,19 * * * cd /path/to/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render
```

## 📋 Cosa Fa lo Script

1. **Download Dati**: Scarica dati freschi da football-data.co.uk
2. **Consolidamento**: Rigenera `dataset_pulito.csv` (storico + stagione corrente)
3. **Features ML**: Rigenera `dataset_features.csv` con rolling statistics
4. **Verifica**: Controlla che dataset sia valido e aggiornato
5. **Reload App**: (opzionale) Triggera `/api/reload_dataset` su Render

## 🔍 Verifica Stato Dataset

### Via Web UI

Vai su: https://pronostici-calcio-professional.onrender.com/dataset_info

Dovresti vedere:
```
📊 Stato Dataset e Modelli
Dataset attivo: data/dataset_pulito.csv
Numero partite: 2960
Ultima partita: 2026-03-22  ✅ AGGIORNATO
```

### Via API

```bash
curl https://pronostici-calcio-professional.onrender.com/api/dataset_info
```

### Via Terminale

```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('data/dataset_pulito.csv')
print(f"Totale: {len(df)} partite")
print(f"Ultima: {df['Date'].max()}")
EOF
```

## 🛠️ Troubleshooting

### "Dataset fermo a data vecchia"

**Causa**: App Render ha dataset cached in memoria

**Soluzione**:
```bash
# Opzione 1: Reload via API
curl -X POST https://pronostici-calcio-professional.onrender.com/api/reload_dataset

# Opzione 2: Script completo
python3 scripts/update_dataset_and_reload.py --reload-render

# Opzione 3: Restart app Render (dashboard web)
```

### "Errore download dati"

**Causa**: football-data.co.uk non disponibile o dati non ancora pubblicati

**Soluzione**:
- Verifica connessione internet
- Controlla https://www.football-data.co.uk/italym.php (manualmente)
- Riprova tra qualche ora (dati pubblicati solitamente domenica sera/lunedì)

### "Timeout reload Render"

**Causa**: App Render in sleep mode (free tier, 15 min idle)

**Soluzione**:
```bash
# 1. Sveglia app prima
curl https://pronostici-calcio-professional.onrender.com/api/dataset_info

# 2. Attendi 30s che si svegli

# 3. Riprova reload
curl -X POST https://pronostici-calcio-professional.onrender.com/api/reload_dataset
```

## 📊 Modifiche al Codice

### 1. Metodo `ricarica_dataset()` (ProfessionalCalculator)

Aggiunto metodo per reload forzato dataset:

```python
def ricarica_dataset(self, data_path='data/dataset_features.csv'):
    """Forza ricaricamento dataset"""
    self.carica_dati(data_path, force_reload=True)
    return {
        'partite_totali': len(self.df_features),
        'ultima_partita': self.df_features['Date'].max()
    }
```

### 2. Endpoint API `/api/reload_dataset`

```python
@app.route('/api/reload_dataset', methods=['POST'])
@limiter.limit("5 per minute")
def api_reload_dataset():
    """Ricarica dataset aggiornato"""
    global calculator
    result = calculator.ricarica_dataset()
    return jsonify({'status': 'success', 'data': result})
```

### 3. Check Timestamp Intelligente

Dataset viene ricaricato automaticamente solo se file modificato più recente del load precedente:

```python
def carica_dati(self, data_path, force_reload=False):
    # Check timestamp file
    if not force_reload and hasattr(self, 'dataset_last_loaded'):
        file_mtime = os.path.getmtime(data_path)
        if file_mtime <= self.dataset_last_loaded:
            return  # Skip reload, già aggiornato
```

## 🎯 Best Practices

### Per Development Locale

Aggiorna manualmente quando serve:
```bash
python3 scripts/update_dataset_and_reload.py
```

### Per Production (Render)

**Opzione A - Cron Job Locale** (Raccomandato):
```bash
# Setup cron che esegue update + reload ogni giorno
crontab -e
# 0 6 * * * cd ~/pronostici_calcio && python3 scripts/update_dataset_and_reload.py --reload-render
```

**Opzione B - GitHub Actions** (Automatico):
```yaml
# .github/workflows/update-dataset.yml
name: Update Dataset Daily
on:
  schedule:
    - cron: '0 6 * * *'  # Ogni giorno alle 6:00 UTC
  workflow_dispatch:  # Manual trigger
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Update dataset
        run: python3 scripts/update_dataset_and_reload.py --reload-render
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/*.csv
          git commit -m "Auto-update dataset $(date +'%Y-%m-%d')" || exit 0
          git push
```

**Opzione C - Manual via API** (Quick fix):
```bash
# Quando noti dataset vecchio
curl -X POST https://pronostici-calcio-professional.onrender.com/api/reload_dataset
```

## 📝 Log Files

Script salva log in `logs/update_dataset.log`:

```bash
# View ultimi aggiornamenti
tail -50 logs/update_dataset.log

# Monitor in real-time
tail -f logs/update_dataset.log

# Count aggiornamenti successo
grep "✅ AGGIORNAMENTO COMPLETATO" logs/update_dataset.log | wc -l
```

## 🔐 Security Notes

- Endpoint `/api/reload_dataset` ha rate limit 5 req/min
- Non espone dati sensibili
- Solo `POST` method (no GET crawlable)
- Log tutti gli accessi

## ✅ Sistema Completamente Automatizzato

Con cron job attivo:
1. ✅ Dati scaricati automaticamente ogni giorno
2. ✅ Dataset rigenerato automaticamente
3. ✅ App Render ricaricata automaticamente
4. ✅ Zero intervento manuale richiesto

**Mai più dataset vecchi!** 🎉
