# 🚀 Render Free Tier - Setup Completo

## ⚠️ Limitazioni Free Tier

- **Sleep dopo 15 minuti** di inattività
- **750 ore/mese** di uptime (sufficiente per uso normale)
- **Nessun background job** (cron tasks non funzionano)

## ✅ Soluzione Implementata

### 1. GitHub Actions Keep-Alive

**File**: `.github/workflows/keep-alive.yml`

- **Ping ogni 10 minuti** → Previene sleep
- **Auto-training giornaliero** alle 3:00 AM
- **Zero costo** (usa runner GitHub gratuiti)

### 2. Setup Secrets GitHub

Vai su: `<<<<<https://github.com/Cosimo77/pronostici-calcio-professional/settings/secrets/actions`>>>>>

Aggiungi secret:

```text
Name: RENDER_DEPLOY_HOOK
Value: <<<<<https://api.render.com/deploy/srv-XXXXXX?key=YYYYYY>>>>>

```

**Come trovare il Deploy Hook:**

1. Vai su Render Dashboard
2. Seleziona il tuo servizio
3. Settings → Deploy Hook
4. Copia l'URL completo

### 3. Workflow Attivo

Una volta pushato, GitHub Actions:

- ✅ Mantiene server attivo 24/7
- ✅ Aggiorna dati Serie A automaticamente
- ✅ Riaddestra modelli ogni giorno
- ✅ Deploya automaticamente su Render

## 🔄 Training Manuale (Opzionale)

Se vuoi triggare training immediato:

```bash
# Da GitHub
Actions → Keep Render Alive & Auto Training → Run workflow

# Locale (richiede server attivo)
python3 allena_modelli_rapido.py
git add models/ data/
git commit -m "🤖 Manual model update"
git push

```

## 📊 Monitoraggio

Verifica che funzioni:

- GitHub Actions: <<<<<<https://github.com/Cosimo77/pronostici-calcio-professional/actions>>>>>>
- Render Logs: Dashboard Render → Logs
- Health Check: <<<<<<https://pronostici-calcio-professional.onrender.com/health>>>>>>

## 💰 Upgrade a Paid (Opzionale)

Se serve:

- **Starter Plan ($7/mese)**: No sleep, always on
- **Background workers**: Cron tasks nativi
- **Più risorse**: CPU/RAM dedicate

## 🎯 Benefici Attuali (Free)

✅ **Zero costi** (100% gratuito)
✅ **Auto-training** modelli giornaliero
✅ **Always available** (grazie a keep-alive)
✅ **Auto-deploy** su git push
✅ **Professional** come paid tier

---

**Status**: 🟢 Production Ready con Free Tier
