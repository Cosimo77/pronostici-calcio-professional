# Debug Database PostgreSQL - Status 15 Feb 2026 21:52

## Cronologia Fix Tentati

### 1. DATABASE_URL Configurazione
- ✅ Database creato: `dpg-d68qngkr85hc73d0jkng-a`
- ✅ DATABASE_URL impostata manualmente (135 chars)
- ✅ Fingerprint: `25c39c95d684`
- ✅ Connection test manuale: **SUCCESSO**

### 2. Problemi Identificati

#### A. DATABASE_URL con testo UI dashboard
```
Error: invalid dsn: missing "=" after "[Dropdown" in connection info string
```
**Fix**: Eliminato valore corrotto e ricreato linking corretto
**Status**: ✅ RISOLTO

#### B. Connection pool non inizializzato
```
Connection succeeded but pool not initialized
```
**Causa**: `init_db()` chiamato all'avvio PRIMA che DATABASE_URL sia disponibile
**Tentativo 1**: Lazy initialization in `get_db_connection()` → ❌ Ricorsione infinita
**Tentativo 2**: Fix ricorsione (test diretto in init_db) → ❌ Ancora fallisce
**Tentativo 3**: Aggressive logging per capire dove fallisce → 🔍 IN CORSO

### 3. Commit History Fix
- `f824925`: Enhanced diagnostic endpoint
- `95ea8e9`: Lazy init in get_db_connection (FALLITO - ricorsione)
- `40251fa`: Lazy init in is_db_available
- `e757d57`: Fix ricorsione (test diretto)
- `a70fe52`: **CURRENT** - Aggressive logging

### 4. Prossimi Step

#### Opzione A: Logs mostrano errore specifico
→ Fix mirato basato su errore

#### Opzione B: Logs mostrano lazy init NON viene mai chiamato
→ Problem diverso: is_db_available() non utilizzato dove serve
→ Fix: Chiamare esplicitamente init_db() in endpoint critici

#### Opzione C: Schema.sql fallisce
→ Fix: Assicurarsi file accessibile e sintassi corretta

## Test Post-Fix

Quando database connected = true, eseguire:

```bash
# 1. Migra CSV→PostgreSQL
python database/migrate_csv_to_postgres.py

# 2. Test persistenza
curl -X POST /api/diario/add {...} 
# Deploy
git commit --allow-empty -m "Test persistence" && git push
# Verifica bet sopravvive

# 3. Clear CSV (opzionale)
rm tracking_giocate.csv
```

## Diagnostics Endpoint

```bash
curl https://pronostici-calcio-pro.onrender.com/api/database/diagnostic
```

Expected dopo fix:
```json
{
  "database_connected": true,
  "total_bets": 0,
  "connection_error": null,
  "database_fingerprint": "25c39c95d684"
}
```

## Collegamenti Utili

- Render Dashboard: https://dashboard.render.com
- Database: pronostici-calcio-db (Frankfurt)
-Service: pronostici-calcio-pro
- Logs: Dashboard → Service → Logs tab
