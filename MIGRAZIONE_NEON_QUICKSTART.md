# 🔄 Migrazione a Neon PostgreSQL - Guida Rapida

**Data**: 4 giugno 2026
**Motivo**: Database Render gratuito scade 8 giugno 2026
**Soluzione**: Neon PostgreSQL FREE permanente (0.5GB, no limiti temporali)

---

## ⚡ Quick Start (10 minuti totali)

### 1️⃣ Esegui Script Automatico

```bash
cd /Users/cosimomassaro/Desktop/pronostici_calcio
./scripts/migrate_render_to_neon.sh
```

Lo script:
- ✅ Esporta dati da Render PostgreSQL
- ✅ Crea backup locale (sicurezza)
- ✅ Ti guida nella creazione account Neon
- ✅ Restore dati su Neon
- ✅ Verifica migrazione completata

### 2️⃣ Aggiorna Render Dashboard

Dopo che lo script completa:

1. Vai su https://dashboard.render.com/
2. Click **pronostici-calcio-pro** → **Environment**
3. Trova **DATABASE_URL**
4. Click **Edit** → Cambia da "From Database" a **"Secret"**
5. Incolla il connection string Neon (fornito dallo script)
6. Click **Save Changes**

Render farà automaticamente **redeploy** (2-3 minuti).

### 3️⃣ Verifica Funzionamento

```bash
# Test health check
curl https://pronostici-calcio-pro.onrender.com/api/health

# Output atteso:
# {
#   "database_connesso": true,
#   "database_records": 2793,
#   "sistema_inizializzato": true
# }
```

### 4️⃣ Cleanup (dopo 7 giorni test)

Quando sei sicuro che tutto funziona:

1. Dashboard Render → **pronostici-calcio-db**
2. Click **Delete** per eliminare database vecchio
3. Conferma eliminazione

---

## 🆘 Problemi Comuni

### Script fail: "psql: command not found"

```bash
# Installa PostgreSQL client
brew install postgresql
```

### Neon connection timeout

Verifica che:
- Region Neon = **Europe (Frankfurt)** (stesso di Render)
- Connection string include `?sslmode=require`

### Database Render vuoto (0 bets)

È normale se hai iniziato da poco! Lo script migra anche database vuoti.

---

## 📊 Confronto Render vs Neon

| Feature | Render Free | Neon Free |
|---------|-------------|-----------|
| **Durata** | ❌ 90 giorni | ✅ **Permanente** |
| **Storage** | 1GB | 0.5GB |
| **Backup** | No | ✅ Automatico (7gg) |
| **Branching** | No | ✅ Illimitato |
| **Costo** | $0 poi $7/mese | ✅ **$0 sempre** |

---

## 💾 Backup Salvato

Lo script salva backup locale:
```
backup_render_YYYYMMDD_HHMMSS.sql
```

**Conserva per 30 giorni** come sicurezza.

---

## ✅ Cosa Cambia nel Codice?

**NIENTE!** Il codice rimane identico:
- Stesso PostgreSQL (Neon usa Postgres 16)
- Stesse queries SQL
- Stesse tabelle (bets, bet_groups)
- Stessa logica applicazione

Cambia solo la **connection string** in `DATABASE_URL`.

---

## 🎯 Vantaggi Neon

1. ✅ **FREE permanente** (no scadenza come Render)
2. ✅ **Branching**: Crea db staging/test istantanei
3. ✅ **Serverless**: Auto-scale, paghi solo compute usato (FREE tier generoso)
4. ✅ **Backup automatici**: Point-in-time recovery incluso
5. ✅ **Performance**: Spesso più veloce di Render Free

---

## 📚 Link Utili

- Neon Dashboard: https://console.neon.tech/
- Neon Docs: https://neon.tech/docs/introduction
- Support: support@neon.tech (risposta <24h)

---

## 🔐 Sicurezza

- ✅ Connection string include password → non committare in Git
- ✅ Render Environment gestisce DATABASE_URL come Secret
- ✅ Neon supporta SSL nativo (`sslmode=require`)
- ✅ Backup automatici Neon cifrati at rest

---

**Domande?** Chiedi prima di procedere!
