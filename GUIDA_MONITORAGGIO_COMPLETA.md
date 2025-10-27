# 🔍 GUIDA COMPLETA AL MONITORAGGIO DEL SISTEMA

## **1. Come Accedere al Monitoraggio**

### **A) Dashboard Web (Più Semplice)** 🖥️
```
https://il-tuo-sito-render.onrender.com/monitoring
```
- **Dashboard visiva in tempo reale**
- **Aggiornamento automatico ogni 30 secondi**
- **Test predizioni direttamente dall'interfaccia**

### **B) API Endpoints** 🔗
```
GET /api/health           → Stato generale del sistema
GET /api/metrics_summary  → Performance e statistiche
GET /api/model_performance → Prestazioni modelli
GET /api/accuracy_report  → Report accuratezza
```

### **C) Script Automatico** 🤖
```bash
python monitor_system.py
```

## **2. Interpretazione degli Indicatori**

### **🟢 SISTEMA SANO**
- **Status**: `healthy`
- **Sistema Inizializzato**: ✅
- **Database Records**: > 1000
- **Squadre Caricate**: > 200
- **Accuratezza Complessiva**: > 50%

### **🟡 ATTENZIONE RICHIESTA**
- **Accuratezza**: 40-50%
- **Cache Entries**: < 50
- **Records Database**: < 500

### **🔴 PROBLEMA CRITICO**
- **Status**: `error`
- **Sistema Inizializzato**: ❌
- **Accuratezza**: < 40%
- **Database Records**: < 100

## **3. Monitoraggio Quotidiano**

### **Controlli Mattutini** 🌅
```bash
# 1. Verifica stato generale
curl https://il-tuo-sito.onrender.com/api/health

# 2. Controlla performance
curl https://il-tuo-sito.onrender.com/api/metrics_summary
```

### **Controlli Settimanali** 📅
1. **Accuratezza Modelli**: Deve rimanere > 50%
2. **Aggiornamento Dati**: Nuove partite nel database
3. **Performance Cache**: Tempo risposta < 2 secondi

## **4. Automazione Completa**

### **Monitoraggio Continuo con Cron** ⏰
```bash
# Aggiungi al tuo crontab (crontab -e)
# Controllo ogni ora
0 * * * * cd /percorso/al/progetto && python monitor_system.py

# Report giornaliero alle 9:00
0 9 * * * cd /percorso/al/progetto && python monitor_system.py --report
```

### **Script per Notifiche** 📱
```python
import requests
import smtplib
from email.mime.text import MIMEText

def invia_alert(messaggio):
    """Invia notifica via email se ci sono problemi"""
    # Configura il tuo servizio email
    pass

def controlla_sistema():
    try:
        response = requests.get('https://il-tuo-sito.onrender.com/api/health')
        data = response.json()
        
        if data['status'] != 'healthy':
            invia_alert(f"ALERT: Sistema non healthy - {data}")
            
        # Controlla accuratezza
        metrics = requests.get('https://il-tuo-sito.onrender.com/api/metrics_summary')
        if metrics.json()['performance']['accuratezza_complessiva'] < 45:
            invia_alert("ALERT: Accuratezza troppo bassa")
            
    except Exception as e:
        invia_alert(f"ERRORE monitoraggio: {e}")

if __name__ == "__main__":
    controlla_sistema()
```

## **5. Interpretazione Metriche Avanzate**

### **Performance Benchmark** 📊
```
ECCELLENTE: > 65% accuratezza
BUONO:      55-65% accuratezza  
ACCETTABILE: 45-55% accuratezza
PROBLEMATICO: < 45% accuratezza
```

### **Mercati Specifici** 🎯
- **Corner**: 55-70% (mercato più affidabile)
- **Cartellini**: 50-65% (dipende dalle squadre)
- **Goal/NoGoal**: 45-60% (più aleatorio)

### **Indicatori di Salute Database** 💾
- **Records Totali**: Cresce costantemente
- **Squadre Caricate**: Stabile (~220-250)
- **Cache Entries**: Riflette l'utilizzo recente

## **6. Risoluzione Problemi Comuni**

### **Sistema Lento** 🐌
```python
# Pulisci cache
import os
import shutil
shutil.rmtree('cache/')
os.makedirs('cache/')
```

### **Accuratezza Bassa** 📉
1. **Controlla dati recenti**: Serve aggiornamento?
2. **Verifica algoritmi**: Sono stati modificati?
3. **Analizza outlier**: Partite anomale?

### **Database Vuoto** 🗄️
```python
# Re-inizializza sistema
python aggiorna_tutto_completo.py
```

## **7. Dashboard Personalizzata**

### **Accesso Rapido** ⚡
Crea bookmark per:
- `https://tuo-sito.com/monitoring` - Dashboard principale
- `https://tuo-sito.com/api/health` - Status rapido
- `https://tuo-sito.com/enterprise` - App principale

### **Monitoraggio Mobile** 📱
La dashboard è responsive e funziona perfettamente su smartphone per controlli in mobilità.

## **8. Best Practices**

### **Frequenza Controlli** ⏱️
- **Manuale**: 2-3 volte al giorno
- **Automatico**: Ogni ora durante giorni di partite
- **Deep Check**: Una volta a settimana

### **Backup e Sicurezza** 🛡️
- **Esporta dati**: Una volta a settimana
- **Test predizioni**: Quotidiano
- **Verifica algoritmi**: Dopo ogni aggiornamento

### **Ottimizzazione Performance** 🚀
- **Cache warming**: Fai qualche predizione dopo riavvio
- **Database cleanup**: Rimuovi dati vecchi periodicamente
- **Monitor memoria**: Controlla utilizzo risorse

---

## **🎯 QUICK START: Come Verificare Tutto Funziona**

### **Controllo Rapido (2 minuti)** ⚡
1. Apri: `https://tuo-sito.onrender.com/monitoring`
2. Clicca "🔄 Aggiorna Tutto"
3. Verifica tutti indicatori verdi
4. Testa una predizione con "🔮 Test Predizione"

### **Se Tutto Verde** ✅
**Il tuo sistema è perfettamente operativo!**

### **Se Qualcosa è Rosso** ❌
1. Controlla i logs su Render
2. Riavvia l'app dal dashboard Render
3. Se persiste, usa `python aggiorna_tutto_completo.py`

---

**💡 CONSIGLIO PRO**: Salva nei bookmark la dashboard di monitoraggio e controllala una volta al giorno. Il sistema è progettato per essere autonomo, ma una verifica quotidiana garantisce prestazioni ottimali!