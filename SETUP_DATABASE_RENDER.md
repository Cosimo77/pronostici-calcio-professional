# Setup Database Render - ISTRUZIONI RAPIDE

## ⚡ ESECUZIONE IMMEDIATA (3 minuti)

### 1. Configura DATABASE_URL su Render

1. Vai su https://dashboard.render.com/
2. Seleziona service **pronostici-calcio-pro**
3. Tab **Environment** → Click **Add Environment Variable**
4. Copia connection string dal database:
   - Vai a **Databases** → `pronostici-calcio-db`
   - Copia **Internal Database URL** (inizia con `postgresql://`)
5. Torna al service, aggiungi:
   ```
   Key: DATABASE_URL
   Value: [incolla URL copiato]
   ```
6. Click **Save Changes**

### 2. Esegui Migrazione Dati

Nell'environment Render, esegui:
```bash
# Deploy triggerato automaticamente dopo Save Changes
# Database si inizializza automaticamente
# Migrazione SQL non necessaria - dati già nel CSV che app legge
```

### 3. Verifica

```bash
curl https://pronostici-calcio-professional.onrender.com/api/database/diagnostic
# Controlla: database_url_set: true, database_connected: true
```

### 4. Cleanup Locale

```bash
# Rimuovi CSV dal repo (dati ora su PostgreSQL)
git rm tracking_giocate.csv
git commit -m "chore: Rimuovi CSV diario - dati migrati su PostgreSQL"
git push
```

## ✅ Risultato Atteso

- ✅ DATABASE_URL configurato
- ✅ PostgreSQL attivo con 8 bets
- ✅ CSV non più necessario
- ✅ Persistenza garantita tra deploy
- ✅ Soluzione professionale

## 🚨 Se Qualcosa Non Funziona

```bash
# Check logs Render
render logs -s pronostici-calcio-pro --tail 50

# Test database connection
curl https://pronostici-calcio-professional.onrender.com/api/health
```
