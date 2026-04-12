#!/bin/bash
# Script per creare PR automaticamente

PR_TITLE="📊 Dataset Update al 06/04/2026 - Production Ready"
PR_BODY="## 🎯 Aggiornamento Dati Serie A

### ✨ Contenuto
- **2970 partite totali** (+4 nuove del 06/04/2026)
- **2753 partite con features ML** (rigenerate)
- Fix ordinamento date DD/MM/YYYY implementato

### 📈 Ultime Partite Incluse
- 06/04: Napoli-Milan 1-0, Juventus-Genoa 2-0, Lecce-Atalanta 0-3, Udinese-Como 0-0
- 05/04: Cremonese-Bologna 1-2, Inter-Roma 5-2, Pisa-Torino 0-1

### 🔧 Fix Tecnici
- scripts/analizza_dati.py: Parsing date con dayfirst=True, format='mixed'
- scripts/feature_engineering.py: Gestione date miste DD/MM/YYYY e YYYY-MM-DD
- Automazione cron testata e funzionante

### ✅ Testing
- [x] Automazione locale testata con successo
- [x] Dataset ordinato cronologicamente
- [x] Features ML validate (2753 records)
- [x] Zero errori di parsing date

### 🚀 Deploy
Al merge, Render farà auto-deploy con rebuild modelli.
Dataset verrà aggiornato da 2743 → 2753 records.

Ready to merge ✅"

# URL-encode del body
ENCODED_BODY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$PR_BODY'''))")

# Apri browser con PR pre-compilata
open "https://github.com/Cosimo77/pronostici-calcio-professional/compare/main...feature/dataset-update-20260407?quick_pull=1&title=$(echo "$PR_TITLE" | sed 's/ /%20/g')&body=$ENCODED_BODY"

echo "🌐 Browser aperto con PR pre-compilata"
echo "📋 Clicca 'Create Pull Request' per completare"
