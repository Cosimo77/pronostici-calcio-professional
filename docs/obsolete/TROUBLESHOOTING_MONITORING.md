# 🚨 TROUBLESHOOTING GUIDE

## Se /monitoring ancora da "Not Found" dopo 10 minuti:

### STEP 1: Verifica Base
```bash
# Test connessione base
curl https://tua-app.onrender.com/

# Test API (dovrebbe funzionare)
curl https://tua-app.onrender.com/api/health
```

### STEP 2: Debug Render
1. Vai su render.com dashboard
2. Trova il tuo servizio
3. Vai su "Logs"
4. Cerca errori tipo:
   - `ImportError`
   - `Template not found`
   - `Route error`

### STEP 3: Riavvio Forzato
1. Su Render dashboard
2. Clicca "Manual Deploy"
3. Seleziona ultimo commit
4. Aspetta 5 minuti

### STEP 4: Verifica File
Se ancora problemi, controlla che esistano:
- `/web/templates/monitoring.html` ✅
- Route `@app.route('/monitoring')` ✅  
- Import `render_template` ✅

### STEP 5: Fallback
Usa le API direttamente:
- `/api/health` - Status
- `/api/metrics_summary` - Performance  
- `/api/model_performance` - Modelli

## 🎯 Il 99% delle volte si risolve aspettando il deployment!