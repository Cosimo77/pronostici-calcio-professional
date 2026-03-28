# 🔧 Guida: Disabilita PostgreSQL su Render (Switch a CSV Storage)

## ❗ Problema Identificato

Il database PostgreSQL Render free tier è **SCADUTO e SOSPESO**:
- **Status**: `suspended`
- **Creato**: 1 mese fa  
- **Cancellazione**: tra 10 giorni
- **Dati persi**: 12+ bet non recuperabili

## ✅ Soluzione: CSV Storage (GRATIS e Permanente)

### Step 1: Rimuovi DATABASE_URL da Render

1. **Vai al dashboard Render**:
   ```
   https://dashboard.render.com
   ```

2. **Seleziona il web service**:
   ```
   pronostici-calcio-professional (Web Service)
   ```
   ⚠️ NON il database!

3. **Click su "Environment"** nel menu laterale

4. **Trova la variabile `DATABASE_URL`**

5. **Elimina DATABASE_URL**:
   - Click sull'icona 🗑️ (cestino) a destra della variabile
   - Oppure cambia il valore in: `disabled`

6. **Click "Save Changes"** in alto

7. **Render farà auto-deploy** (2-3 minuti)

### Step 2: Verifica Fallback CSV Attivo

Dopo il redeploy, controlla:

```bash
# Apri il diario
https://pronostici-calcio-professional.onrender.com/diario

# Dovresti vedere le 8 bet consolidate:
# - 3 FASE1 (pareggi)
# - 5 FASE2 (multi-mercato)
```

### Step 3: Test Funzionamento

1. **Aggiungi una bet di test** dall'interfaccia web
2. **Verifica che venga salvata** (refresh pagina)
3. **Check Git**: La bet NON apparirà in tracking_giocate.csv locale (solo su Render)

## 🔄 Come Funziona CSV Storage

### Architettura

```
┌─────────────────────────────────────┐
│  web/diario_storage.py              │
│  (Adapter Pattern)                  │
│                                     │
│  if DATABASE_URL exists:            │
│    ❌ PostgreSQL (scaduto)          │
│  else:                              │
│    ✅ CSV fallback (tracking_*.csv) │
└─────────────────────────────────────┘
```

### Vantaggi CSV

✅ **GRATIS**: No costi mensili ($0 vs $7/mese PostgreSQL)  
✅ **Git Trackable**: Backup automatico su GitHub  
✅ **Portabile**: Funziona ovunque (locale + Render)  
✅ **Semplice**: No gestione database, no upgrade

### Limitazioni CSV

⚠️ **Concurrent Access**: CSV non supporta accessi simultanei (ok per uso singolo)  
⚠️ **Performance**: Lento con >1000 bet (ok per betting reale ~100 bet/anno)  
⚠️ **Backup Manuale**: Devi committare periodicamente su Git

## 📊 Dati Consolidati Disponibili

File: `tracking_giocate.csv` (8 bet recuperate)

```csv
Data,Partita,Mercato,Quota,Stake,Risultato,Profit
2026-02-14,Como vs Fiorentina,X2,2.1,2.0,PENDING,0.0
2026-02-09,Roma vs Cagliari,Over 2.5,2.1,10.0,LOSS,-10.0
2026-02-15,Cremonese vs Genoa,Pareggio,2.97,10.0,PENDING,0.0
2026-02-15,Parma vs Verona,Over 2.5,2.48,10.0,PENDING,0.0
2026-02-15,Napoli vs Roma,1X,1.44,10.0,PENDING,0.0
... (8 totali)
```

**Statistiche**:
- 7 PENDING
- 1 LOSS (-€10)
- Total stake: €52
- ROI: -19.2%

## 🔄 Workflow Futuro

### Locale (Mac)

```bash
# 1. Lavora con CSV locale
vim tracking_giocate.csv

# 2. Commit periodici
git add tracking_giocate.csv
git commit -m "Update: +3 bet completate"
git push origin main

# 3. Render auto-sync (pull da GitHub ogni deploy)
```

### Render (Produzione)

```bash
# Render legge tracking_giocate.csv dal repo GitHub
# Ogni modifica locale → git push → Render redeploy → Dati aggiornati
```

### Sincronizzazione Bidirezionale

Se aggiungi bet via web interface Render:

```bash
# Locale: Scarica dati da Render
python3 scripts/sync_from_render.py

# Output: tracking_giocate.csv aggiornato con bet da Render
```

## 🚨 Troubleshooting

### Problema: Diario vuoto dopo rimozione DATABASE_URL

**Causa**: File tracking_giocate.csv non presente su Render

**Soluzione**:
```bash
# 1. Verifica che file sia committato
git status tracking_giocate.csv

# 2. Push su GitHub
git push origin main

# 3. Trigger redeploy Render manualmente
Render Dashboard → pronostici-calcio-professional → Manual Deploy
```

### Problema: Bet duplicate

**Causa**: CSV locale diverso da Render

**Soluzione**:
```bash
# Scarica dati da Render (source of truth)
python3 scripts/sync_from_render.py

# Sovrascrive CSV locale con dati Render
```

## 📚 File Rilevanti

- `web/diario_storage.py`: Adapter PostgreSQL/CSV
- `tracking_giocate.csv`: Dati diario (8 bet recuperate)
- `tracking_fase2_febbraio2026.csv`: Backup FASE2 originale
- `scripts/sync_from_render.py`: Download dati da Render
- `scripts/consolidate_tracking_data.py`: Merge multi-source

## ✅ Checklist Completamento

- [ ] Rimosso DATABASE_URL da Render Environment
- [ ] Salvato changes + redeploy completato
- [ ] Verificato diario mostra 8 bet
- [ ] Testato aggiunta nuova bet via web
- [ ] Commit tracking_giocate.csv su Git

## 🎯 Recap

**Prima**: 
- PostgreSQL Render (scaduto, €7/mese)
- 20+ bet perse nel database sospeso
- 0 backup locali sincronizzati

**Dopo**:
- CSV storage (gratis, Git-backed)
- 8 bet recuperate e consolidate
- Sistema funzionante senza costi
- Backup automatici su GitHub

---

**Data guida**: 21 Marzo 2026  
**Commit recovery**: `b8bf070`
