# 🔧 GUIDA CONFIGURAZIONE AUTOMAZIONE RENDER

## 🚨 PROBLEMA ATTUALE

**Situazione:**
- Locale: 2846 partite (ultima: 2026-01-08) ✅
- Render: 2815 partite (fermo al: 2026-01-11) ❌
- Automazione: Dice "running: true" ma NON aggiorna realmente

**Causa:**
Sistema "hybrid" - automazione locale NON attiva + Render NON ha cron jobs nel free tier

---

## ✅ SOLUZIONE: 2 OPZIONI

### OPZIONE 1: Automazione Locale + Push GitHub (CONSIGLIATA)

**Setup cron job macOS:**

```bash
# 1. Apri crontab
crontab -e

# 2. Aggiungi questa riga (esegue ogni giorno alle 06:00)
0 6 * * * /Users/cosimomassaro/Desktop/pronostici_calcio/automation_cron.sh >> /Users/cosimomassaro/Desktop/pronostici_calcio/logs/cron.log 2>&1

# 3. Salva e esci (ESC :wq)

# 4. Verifica cron installato
crontab -l
```

**Come funziona:**
1. Cron esegue `automation_cron.sh` ogni giorno alle 06:00
2. Script scarica nuovi dati da football-data.co.uk
3. Fa commit e push su GitHub
4. Render rileva push → deploy automatico → dati aggiornati

**Pros:**
- ✅ Gratuito (usa Mac sempre acceso)
- ✅ Full control
- ✅ Funziona con Render free tier

**Cons:**
- ❌ Mac deve essere acceso alle 06:00
- ❌ Manuale se Mac spento

---

### OPZIONE 2: GitHub Actions (CI/CD Cloud)

**Setup workflow automatico:**

Crea file `.github/workflows/auto-update.yml`:

```yaml
name: Auto Update Dati

on:
  schedule:
    # Esegui ogni giorno alle 06:00 UTC
    - cron: '0 6 * * *'
  workflow_dispatch: # Permette esecuzione manuale

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repo
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dipendenze
      run: pip install -r requirements.txt
    
    - name: Scarica nuovi dati
      run: python3 scripts/scraper_dati.py
    
    - name: Commit e push
      run: |
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add data/
        git commit -m "🔄 Auto-update dati $(date +'%Y-%m-%d')" || echo "No changes"
        git push
```

**Pros:**
- ✅ Totalmente automatico
- ✅ Cloud-based (non serve Mac acceso)
- ✅ Gratuito (2000 minuti/mese GitHub)
- ✅ Log visibili su GitHub

**Cons:**
- ❌ Richiede setup GitHub Actions
- ❌ Dipende da GitHub

---

## 🛠️ FIX IMMEDIATO (Manuale)

**Per aggiornare SUBITO Render:**

```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio

# 1. Forza aggiornamento dati
python3 scripts/scraper_dati.py

# 2. Commit modifiche (se ce ne sono)
git add data/
git commit -m "Update dati $(date +'%Y-%m-%d')"

# 3. Push → trigger Render deploy
git push origin main

# Render ricarica automaticamente in ~2 minuti
```

**Verifica deploy Render:**
```bash
# Attendi 2-3 minuti, poi:
curl -s https://pronostici-calcio-professional.onrender.com/api/health | grep database_records
```

---

## 📊 MONITORING AUTOMAZIONE

**Verifica locale:**
```bash
# Log cron
tail -f /Users/cosimomassaro/Desktop/pronostici_calcio/logs/cron.log

# Ultimo timestamp automazione
cat /Users/cosimomassaro/Desktop/pronostici_calcio/logs/last_automation.txt
```

**Verifica Render:**
```bash
# Partite caricate
curl -s https://pronostici-calcio-professional.onrender.com/api/health | python3 -c "import json,sys; print(json.load(sys.stdin)['database_records'])"

# Ultimo aggiornamento
curl -s https://pronostici-calcio-professional.onrender.com/api/automation_status | python3 -c "import json,sys; print(json.load(sys.stdin)['last_daily_update'])"
```

---

## 🎯 RACCOMANDAZIONE

**Per te: OPZIONE 2 (GitHub Actions)**

Perché:
1. Mac potrebbe non essere sempre acceso alle 06:00
2. Totalmente automatico, zero manutenzione
3. Gratis e affidabile
4. Log visibili su GitHub

**Setup in 5 minuti:**

1. Crea directory:
```bash
mkdir -p /Users/cosimomassaro/Desktop/pronostici_calcio/.github/workflows
```

2. Crea file workflow (vedi OPZIONE 2 sopra)

3. Commit e push:
```bash
git add .github/
git commit -m "Add GitHub Actions auto-update"
git push origin main
```

4. Attiva workflow su GitHub:
   - Vai su repo → Actions tab
   - Trovi "Auto Update Dati"
   - Click "Enable workflow"

**Done!** Da domani aggiornamento automatico ogni giorno alle 06:00 UTC (07:00 Italia).

---

## ❓ FAQ

**Q: Perché Render non ha cron?**
A: Free tier Render non supporta cron jobs. Solo paid plans.

**Q: I dati vecchi su Render impattano predizioni?**
A: Minimamente. 31 partite su 2815 = 1.1% differenza. Sistema robusto.

**Q: Posso testare GitHub Actions ora?**
A: Sì! Vai su repo GitHub → Actions → "Auto Update Dati" → "Run workflow"

**Q: Quanto costa GitHub Actions?**
A: Gratis fino a 2000 minuti/mese. Questo workflow usa ~5 min/giorno = 150 min/mese.

---

**Creato:** 14 Gennaio 2026
**Status:** Automazione NON configurata (richiede scelta OPZIONE 1 o 2)
