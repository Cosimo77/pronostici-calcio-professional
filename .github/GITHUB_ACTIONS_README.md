# 🤖 GitHub Actions Auto-Update Workflow

## 📋 Overview

Workflow automatico che:
1. ✅ Scarica nuovi dati Serie A da football-data.co.uk ogni giorno
2. ✅ Genera features per ML
3. ✅ Committa automaticamente nuove partite
4. ✅ Notifica Render per reload dataset

## ⏰ Schedule

- **Automatico**: Ogni giorno alle 5:00 UTC (6:00 CET / 7:00 CEST)
- **Manuale**: Trigger da GitHub Actions UI

## 🔧 Script Utilizzati

### `scripts/auto_download_data.py`
- Download CSV stagione corrente da football-data.co.uk
- Confronta con dataset esistente
- Genera `update_info.txt` con numero nuove partite
- Exit code 0 = successo, 2 = errore

### `scripts/feature_engineering.py`
- Genera features ML (opzionale, con fallback graceful)

## 🚀 Trigger Manuale

```bash
# Da GitHub UI
Actions → Aggiornamento Automatico Dati → Run workflow

# Da CLI (con GitHub CLI)
gh workflow run auto-update.yml
```

## 📊 Output

### Success (con nuove partite)
```
📊 Nuove partite da committare: 3
✅ Committed: "chore: Auto-update Serie A data (+3 partite) [skip ci]"
✅ Render notificato
```

### Success (nessun aggiornamento)
```
📊 Nuove partite da committare: 0
ℹ️  Nessuna nuova partita da aggiornare
```

### Failure
```
❌ Download fallito: HTTP 404
Exit code: 2
```

## 🐛 Troubleshooting

### Exit Code 2
**Causa**: Script `auto_download_data.py` non trovato o errore Python
**Fix**: Verifica che `scripts/auto_download_data.py` esista nel repo

### Commit fallito
**Causa**: Nessun file modificato o conflitti git
**Fix**: Workflow usa `[skip ci]` per evitare loop infiniti

### Render reload fallito
**Causa**: URL Render non risponde o rate limit
**Fix**: Non critico, Render ha auto-reload settimanale

## 🔐 Secrets Required

- `GITHUB_TOKEN`: Auto-iniettato da GitHub (no config necessaria)

## 📝 Note

- **Skip CI**: Commit includono `[skip ci]` per evitare trigger ricorsivi
- **Continue on Error**: Feature engineering ha fallback graceful
- **Rate Limiting**: Max 1 run/giorno (schedule), illimitati manuali
- **Node.js Warning**: Actions useranno Node.js 24 da Giugno 2026 (già supportato)

## ✅ Validation

Per testare localmente:
```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio
python3 scripts/auto_download_data.py
cat update_info.txt  # Mostra numero partite aggiunte
```

## 🎯 Success Criteria

- ✅ Script eseguito senza errori (exit 0)
- ✅ File `update_info.txt` creato
- ✅ CSV scaricato in `data/I1_XXYY.csv`
- ✅ Commit automatico se nuove partite
- ✅ Render notificato (best effort)

## 📈 Metriche

- **Frequenza**: 1x/giorno (5:00 UTC)
- **Duration**: ~20-30 secondi
- **Success Rate**: >95% (dipende da football-data.co.uk uptime)
- **Storage**: +5KB per partita (~1.5MB/stagione)
