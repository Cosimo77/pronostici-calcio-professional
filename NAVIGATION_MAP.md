# 🗺️ Mappa Navigazione Sistema Pronostici Serie A

## 📊 Struttura Pagine Web

### **Navbar Unificata** (`web/templates/navbar.html`)
Navbar professionale presente in **tutte le pagine** con:
- Logo e brand
- Menu principale con icone
- Dropdown per analisi avanzate
- Theme toggle (dark/light)
- Quick stats (ultimo aggiornamento)
- **Auto-evidenziazione** pagina attiva

---

## 🌐 Pagine Principali

### 1️⃣ **Dashboard** (`/` → `enterprise_v2.html`)
**Funzione**: Centro di controllo principale
- **Predizioni singole** con form squadre
- **Monitoraggio performance** ML
- **Value Betting** overview
- **Prossime partite** con quote live
- **Statistiche sistema** in tempo reale

**Link navbar**: 🏠 Dashboard

---

### 2️⃣ **Giornata** (`/giornata` → `giornata.html`)
**Funzione**: Pronostici completi giornata corrente
- **Tutte le partite** della giornata
- **14+ mercati** per ogni match (1X2, Over/Under, GG/NG, DC, ecc.)
- **Badge validazione** FASE1-5 (verde, blu, viola, arancione, rosa)
- **TOP 3 Opportunità** filtrate
- **Value Betting** con EV% visibile

**Link navbar**: 📅 Giornata

**Validazioni visibili**:
- 🟢 **FASE1**: Pareggi (quote 2.8-3.5, EV 25-60%)
- 🔵 **FASE2**: Vittorie Casa/Trasferta (quote 1.5-2.5, EV 25-60%)
- 🟣 **FASE3**: Over/Under 2.5 (quote 1.75-2.25, EV 30-60%)
- 🟠 **FASE4**: Goal/No Goal (quote ≤2.0, EV 35-70%)
- 🩷 **FASE5**: Double Chance (quote ≤1.6, EV 35-70%)

---

### 3️⃣ **Diario Betting** (`/diario` → `diario_betting.html`)
**Funzione**: Tracking professionale scommesse
- **Aggiungi predizioni** manualmente o automatiche
- **Tracking real-time** profit/loss
- **Gestione bankroll** con Kelly Criterion
- **Statistiche dettagliate** (ROI, Win Rate, Streak)
- **Multiple** e **Singole** separate
- **Equity curve** grafico

**Link navbar**: 📔 Diario

**Sezioni**:
- Tab **Singole**: Scommesse 1X2, O/U, GG/NG
- Tab **Multiple**: Combo 2-5 eventi
- Tab **Statistiche**: ROI per mercato, accuracy, drawdown

---

### 4️⃣ **Monitoraggio** (`/monitoring` → `monitoring_v2.html`)
**Funzione**: Dashboard metriche sistema
- **Performance ML** (accuracy, precision, recall)
- **ROI per mercato** (FASE1-5)
- **Grafici interattivi** Chart.js
- **Cache performance** (hit rate, speedup)
- **Health check** sistema
- **Accuracy live** tracking

**Link navbar**: 📊 Analisi → Monitoraggio

**Charts disponibili**:
- ROI by Market (bar chart)
- Accuracy Trend (line chart)
- Win Rate by Fase (doughnut)
- ML Predictions vs Actual (scatter)

---

### 5️⃣ **Automazione** (`/automation` → `automation_status.html`)
**Funzione**: Status e controllo automazione
- **Ultimo aggiornamento** dati (auto-update.yml)
- **Ultimo retrain** modelli (weekly-retrain.yml)
- **Deploy status** Render
- **Pulsante deploy** manuale
- **GitHub Actions** status
- **Logs** automazione

**Link navbar**: 📊 Analisi → Automazione

**Azioni disponibili**:
- 🚀 **Deploy to Render** (rate limited 5/ora)
- 🔄 **Force Update** dati
- 🧠 **Force Retrain** modelli
- 📥 **Download Tracking** CSV

---

## 🔄 Flusso di Lavoro Utente

### **Scenario 1: Value Betting Daily**
1. **Dashboard** (`/`) → Controlla sistema attivo
2. **Giornata** (`/giornata`) → Vedi TOP 3 opportunità validate
3. **Diario** (`/diario`) → Traccia scommesse piazzate
4. **Monitoraggio** (`/monitoring`) → Verifica ROI accumulato

### **Scenario 2: Analisi Singola Partita**
1. **Dashboard** (`/`) → Form "Predizione Singola"
2. Seleziona squadre → Ottieni 14 mercati
3. Confronta con **Giornata** (`/giornata`) per quote reali
4. Salva in **Diario** (`/diario`)

### **Scenario 3: System Admin**
1. **Automazione** (`/automation`) → Verifica ultimo update
2. Se outdated → Click **Deploy to Render**
3. **Monitoraggio** (`/monitoring`) → Controlla accuracy post-retrain
4. **Dashboard** (`/`) → Verifica "Quick Stats"

---

## 🎨 Design System

### **Colori Validazione**
- `badge-fase1`: Verde (`#10b981`) - Pareggi conservativi
- `badge-fase2`: Blu (`#3b82f6`) - Vittorie probabili
- `badge-fase3`: Viola (`#8b5cf6`) - Over/Under
- `badge-fase4`: Arancione (`#f59e0b`) - Goal/No Goal
- `badge-fase5`: Rosa (`#ec4899`) - Double Chance

### **Temi**
- **Dark** (default): Gradiente blu scuro (`#1e3c72` → `#2a5298`)
- **Light**: Gradiente grigio chiaro (`#f5f7fa` → `#c3cfe2`)
- Toggle: Icona luna/sole (localStorage persistente)

### **Componenti Comuni**
- **Glass Card**: Backdrop blur, bordi sfumati
- **Gradient Buttons**: Oro/rosso per azioni primarie
- **Skeleton Loaders**: Animazione shimmer durante fetch
- **Toast Notifications**: Top-right, auto-dismiss 3s

---

## 🔗 Link Diretti

| Pagina | URL | Alias |
|--------|-----|-------|
| Dashboard | `/` | `/enterprise`, `/value-betting`, `/analysis` |
| Giornata | `/giornata` | `/upcoming`, `/upcoming_matches` |
| Diario | `/diario` | `/diario-betting`, `/tracking` |
| Monitoraggio | `/monitoring` | `/monitoring/dashboard` |
| Automazione | `/automation` | - |

---

## 📱 Responsive Design

Tutte le pagine sono **mobile-friendly** con breakpoints:
- **Desktop**: >1200px (3-4 colonne)
- **Tablet**: 768-1199px (2 colonne)
- **Mobile**: <768px (1 colonna, navbar collapsible)

---

## 🚀 Quick Actions (da qualsiasi pagina)

### **Navbar sempre visibile**:
- Click **Logo** → Torna alla Dashboard
- **Giornata** → Vedi opportunità oggi
- **Diario** → Controlla profit/loss
- **Analisi** → Dropdown monitoraggio/automazione
- **Theme Toggle** → Cambia tema dark/light

### **Footer Link** (su tutte le pagine):
- Disclaimer gioco responsabile
- Link SOS Azzardo (800.558.822)
- Numero Verde ADM

---

## 🛠️ Manutenzione

### **Aggiungere Nuova Pagina**
1. Crea template in `web/templates/nuova_pagina.html`
2. Aggiungi Bootstrap 5.3.3 + Bootstrap Icons se assente
3. **Subito dopo `<body>`**: `{% include 'navbar.html' %}`
4. Aggiungi route in `web/app_professional.py`:
   ```python
   @app.route("/nuova_pagina")
   def nuova_pagina():
       return render_template("nuova_pagina.html")
   ```
5. **Aggiorna navbar.html**: aggiungi voce menu
6. Test navigazione completa

### **Modificare Navbar**
- Modifica **solo** `web/templates/navbar.html`
- Cambiamenti si riflettono su **tutte** le pagine
- Restart Flask per vedere modifiche

---

## ✅ Checklist Post-Deploy

- [ ] Navbar visibile su tutte le pagine
- [ ] Pagina attiva evidenziata in oro
- [ ] Theme toggle funzionante
- [ ] Tutti i link navbar portano a pagine corrette
- [ ] Responsive su mobile (test navbar collapse)
- [ ] Quick stats aggiornate (ultimo update)
- [ ] Nessun errore console browser
- [ ] Bootstrap JS caricato (dropdown funzionano)

---

**Versione**: 2.8.1
**Ultimo aggiornamento**: 09/05/2026
**Autore**: Sistema Professionale Pronostici Serie A
