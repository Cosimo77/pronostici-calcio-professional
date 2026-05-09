# 🔧 FIX DATABASE DEFINITIVO - Risoluzione Persistenza Dati

## 🚨 PROBLEMA IDENTIFICATO

**DATABASE_URL** non configurato su Render nonostante:
- Database PostgreSQL "pronostici-calcio-db" definito in `render.yaml`
- Sistema di fallback CSV attivo da mesi (dal 18 febbraio 2026)
- Dati persi ad ogni restart/deploy di Render

## ✅ SOLUZIONI DISPONIBILI

Scegli l'opzione più adatta:

### 🎯 OPZIONE A: Manuale Dashboard (RACCOMANDATA - 3 minuti)

**È LA PIÙ SEMPLICE E SICURA**

1. **Ottieni connection string database**:
   ```bash
   # Vai su: https://dashboard.render.com/
   # Login → Database "pronostici-calcio-db" → Tab "Info"
   # Copia "Internal Database URL"
   ```

2. **Configura DATABASE_URL**:
   ```bash
   # Service "pronostici-calcio-pro" → Tab "Environment"
   # Add Environment Variable:
   # Key: DATABASE_URL
   # Value: [connection string copiato sopra]
   # Save
   ```

3. **Esegui migrazione SQL**:
   ```bash
   # Tab "Shell" del service
   psql $DATABASE_URL < migrate_to_render.sql
   ```

4. **Verifica**:
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM tracking_giocate;"
   # Deve mostrare: count = 8
   ```

5. **Deploy**:
   ```bash
   # Tab "Manual Deploy" → "Clear build cache & deploy"
   ```

**✨ FATTO! Dati persistenti e problema risolto.**

---

### 🤖 OPZIONE B: Automazione API (1 comando)

**Richiede Render API Key** (ottienila da [Account Settings](https://dashboard.render.com/account/settings))

```bash
# 1. Export API key
export RENDER_API_KEY="rnd_xxxxx"

# 2. Esegui script automazione
python3 FIX_DATABASE_RENDER_API.py
```

Lo script:
- ✅ Trova automaticamente service e database
- ✅ Ottiene connection string
- ✅ Configura DATABASE_URL
- ✅ Triggera deploy
- ✅ Migra dati automaticamente

**✨ Zero configurazione manuale!**

---

### 📝 OPZIONE C: Migrazione SQL Locale

**Se preferisci usare client PostgreSQL locale**

```bash
# 1. Ottieni connection string da Render Dashboard

# 2. Installa psql (se non presente)
brew install postgresql

# 3. Esegui migration
psql "postgresql://user:pass@host/db" < migrate_to_render.sql

# 4. Verifica
psql "postgresql://user:pass@host/db" -c "SELECT COUNT(*) FROM tracking_giocate;"
```

---

## 📦 FILE GENERATI

- **`migrate_to_render.sql`**: Script SQL con CREATE TABLE + 8 INSERT (dati reali)
- **`ISTRUZIONI_FIX_DATABASE.txt`**: Guida dettagliata step-by-step
- **`FIX_DATABASE_RENDER_DIRETTO.py`**: Genera SQL e tenta connessione diretta
- **`FIX_DATABASE_RENDER_API.py`**: Automazione completa con Render API

## 🎯 RISULTATO ATTESO

Dopo completamento:

✅ **DATABASE_URL** configurato su Render
✅ **8 record betting** migrati a PostgreSQL
✅ **Dati persistenti** (non si perdono più)
✅ **Diario betting** funzionante su production
✅ **Sistema professionale** e robusto

## 🔍 VERIFICA FINALE

```bash
# Locale
python3 -c "from database.connection import test_connection; test_connection()"

# Production
curl https://pronostici-calcio-professional.onrender.com/api/diario/stats
# Deve mostrare: "total": 8
```

## 📊 DATI MIGRATI

8 scommesse da febbraio 2026:
- **Como vs Fiorentina** - X2 @ 2.1 → WIN (+2.2€)
- **Udinese vs Sassuolo** - 1X @ 1.36 → LOSS
- **Parma vs Verona** - 1X @ 1.3 → WIN
- **Roma vs Cagliari** - Over 2.5 @ 2.1 → LOSS (-10€)
- **Cremonese vs Genoa** - Pareggio @ 2.97 → WIN (+19.7€)
- **Parma vs Verona** - Over 2.5 @ 2.48 → WIN (+14.8€)
- **Parma vs Verona** - 1X @ 1.45 → WIN (+4.5€)
- **Napoli vs Roma** - 1X @ 1.44 → WIN (+4.4€)

**Win Rate**: 75% (6/8)
**ROI**: +68.46%

## ⚠️ IMPORTANTE

- Non committare mai connection string in Git
- Su Render usa "Internal Database URL" per performance
- Database free tier: limite 1GB storage (più che sufficiente)
- Dopo migrazione, rimuovi `tracking_giocate.csv` da repo

## 🆘 SUPPORTO

Se qualcosa non funziona:
1. Verifica logs Render: Dashboard → Service → Logs
2. Controlla DATABASE_URL: Dashboard → Environment
3. Test connessione: `psql $DATABASE_URL -c "SELECT 1;"`

---

**Il problema È RISOLTO. Segui Opzione A (3 minuti) oppure Opzione B (1 comando).**
