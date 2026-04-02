# 🚀 Roadmap Miglioramenti Sistema Value Betting

## 📊 Stato Attuale (14 Feb 2026)
- ✅ Dashboard opportunità FASE2 (sweet spot 20-25% EV)
- ✅ Diario betting professionale (tracking, editing, statistiche)
- ✅ Quote formattate 2 decimali (standard bookmaker)
- ✅ Verifica manuale quota su prompt
- ✅ Performance ottimizzate (<90ms DOMContentLoaded)
- ✅ ROI backtest validato: +21.8% DC, +7.2% Pareggi
- ✅ **2 puntate pending** attive (Como vs Fiorentina, Parma vs Verona)

---

## 🎯 Miglioramenti Prioritari (Impatto/Effort)

### **TIER 1 - Quick Wins (1-2 ore implementazione)**

#### 1. **Shrinkage Factor Adattivo** 🔥 ALTA PRIORITÀ
**Problema**: EV_Realistico usa shrinkage fisso `ev_modello / 3.5` (~70%)  
**Soluzione**: Calcola shrinkage DINAMICO dai risultati reali del diario

```python
# Esempio logica
def calcola_shrinkage_adattivo():
    """Calcola shrinkage basato su ROI reale vs modello"""
    df = pd.read_csv('tracking_giocate.csv')
    df_closed = df[df['Risultato'].isin(['WIN', 'LOSS'])]
    
    if len(df_closed) < 10:
        return 0.35  # Default conservativo (shrinkage 65%)
    
    # Confronta EV previsto vs profit reale
    ev_medio_modello = df_closed['EV_Modello'].str.replace('%', '').astype(float).mean()
    roi_reale = (df_closed['Profit'].sum() / len(df_closed)) * 100
    
    shrinkage = max(0.15, min(0.50, roi_reale / ev_medio_modello))
    return shrinkage
```

**Impatto**:
- EV più accurato dopo 20+ bet
- Sistema auto-calibrante (machine learning pratico)
- Riduce gap modello-realtà automaticamente

**File da modificare**: `web/app_professional.py` (linea ~1750 calcolo EV_Realistico)

---

#### 2. **Grafici Equity Curve nel Diario** 📈
**Cosa**: Chart.js mostra profit cumulativo nel tempo  
**Dove**: Tab "Statistiche" nel diario

```javascript
// Equity curve
const equityCurve = completedBets.map((bet, i) => ({
    x: i + 1,
    y: completedBets.slice(0, i + 1).reduce((sum, b) => sum + b.profit, 0)
}));

new Chart(ctx, {
    type: 'line',
    data: {datasets: [{label: 'Profit Cumulativo', data: equityCurve}]}
});
```

**Impatto**:
- Visual feedback performance (motivazione)
- Identifica trend (winning/losing streaks)
- Evidenzia drawdown visivamente

**File da modificare**: `web/templates/diario_betting.html` (nuova tab "📊 Grafici")

---

#### 3. **Kelly Criterion per Stake Ottimale** 💰
**Cosa**: Calcola stake matematicamente ottimale invece di flat €2  
**Formula**: `stake% = (p * q - 1) / (q - 1)` dove p=prob_win, q=quota

```python
def calcola_kelly_stake(probabilita, quota, bankroll, kelly_fraction=0.25):
    """
    Kelly Criterion con fraction conservativa (1/4 Kelly)
    """
    p = probabilita
    q = quota
    b = q - 1  # profitto netto per €1
    
    kelly = (p * b - (1 - p)) / b
    kelly_conservativo = kelly * kelly_fraction  # 1/4 Kelly = più sicuro
    
    stake = max(0, min(bankroll * kelly_conservativo, bankroll * 0.05))  # Max 5% bankroll
    return round(stake, 2)
```

**Impatto**:
- Massimizza crescita bankroll long-term
- Protegge da overbetting (max 5% singola bet)
- Professionale come veri value bettor

**File**: nuovo `scripts/kelly_calculator.py` + integrazione dashboard

---

### **TIER 2 - Medium Priority (3-6 ore)**

#### 4. **Notifiche Telegram** 📱
**Cosa**: Bot Telegram invia alert quando nuova opportunità FASE2  
**Setup**: `pip install python-telegram-bot`

```python
import telegram

bot = telegram.Bot(token='TUO_TOKEN')

async def notify_new_opportunity(partita, mercato, quota, ev):
    message = f"""
🚨 NUOVA OPPORTUNITÀ
    
Partita: {partita}
Mercato: {mercato}
Quota: {quota}
EV: +{ev}%
    
👉 http://localhost:5008/upcoming_matches
"""
    await bot.send_message(chat_id='TUO_CHAT_ID', text=message)
```

**Impatto**:
- Zero opportunità perse (alert immediato)
- Mobile-friendly (Telegram sempre a portata)
- Professional workflow (come tipster pro)

**File**: `scripts/telegram_notifier.py` + integrazione upcoming_matches

---

#### 5. **Export Excel Avanzato** 📊
**Cosa**: Esporta diario con analytics professionale (grafici, pivot, formule)

```python
import openpyxl
from openpyxl.chart import LineChart

def export_diario_excel():
    """Export diario con grafici Excel nativi"""
    wb = openpyxl.Workbook()
    
    # Sheet 1: Raw data
    ws_data = wb.active
    ws_data.title = 'Tracking Giocate'
    
    # Sheet 2: Analytics
    ws_analytics = wb.create_sheet('Analytics')
    # Formule: =SUM(Profit), =AVERAGE(ROI), etc.
    
    # Sheet 3: Grafici equity curve
    ws_charts = wb.create_sheet('Grafici')
    chart = LineChart()
    # ...
    
    wb.save('diario_export.xlsx')
```

**Impatto**:
- Condividi risultati (screenshot professionali)
- Analisi offline Excel (power user)
- Backup automatico fuori CSV

**File**: `scripts/export_excel.py` + pulsante nel diario

---

#### 6. **Mobile Responsive Dashboard** 📱
**Cosa**: Media queries CSS per smartphone/tablet

```css
@media (max-width: 768px) {
    .opp-card {
        width: 100%;
        margin: 10px 0;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .opp-header {
        font-size: 14px;
    }
}
```

**Impatto**:
- Controlla opportunità da mobile (ovunque)
- Aggiungi puntate da smartphone
- UX moderna (aspettativa 2026)

**File**: `web/templates/upcoming_matches.html` + `diario_betting.html` (nuove media queries)

---

### **TIER 3 - Advanced (1-2 giorni)**

#### 7. **Auto-Scraping Quote Sisal** 🤖
**Cosa**: Selenium/Playwright scraping automatico quote Sisal real-time  
**Problema**: Quote cambiano rapidamente, verifica manuale lenta

```python
from playwright.sync_api import sync_playwright

def scrape_sisal_odds(partita):
    """Scraping quote Sisal automatico"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.sisal.it/scommesse/calcio/...')
        
        # Trova partita
        quote_element = page.locator(f'text="{partita}"')
        odds_1x = quote_element.locator('.dc-1x').text_content()
        
        return float(odds_1x)
```

**Impatto**:
- **ZERO verifica manuale** (automazione totale)
- Quote sempre aggiornate (real-time)
- Confronto auto modello vs Sisal

**Rischio**: Sisal può cambiare HTML, servono fallback  
**File**: `scripts/sisal_scraper.py` + integrazione dashboard

---

#### 8. **Multi-Bookmaker Comparison** 🎲
**Cosa**: Confronta quote Sisal vs Bet365 vs Snai → scegli la migliore

```python
def trova_best_odds(partita, mercato):
    """Trova quota migliore tra bookmaker"""
    odds_sisal = scrape_sisal(partita, mercato)
    odds_bet365 = scrape_bet365(partita, mercato)
    odds_snai = scrape_snai(partita, mercato)
    
    best = max([
        ('Sisal', odds_sisal),
        ('Bet365', odds_bet365),
        ('Snai', odds_snai)
    ], key=lambda x: x[1])
    
    return best  # ('Bet365', 2.45)
```

**Impatto**:
- +5-10% profit extra (migliori quote = ROI superiore)
- Arbitraggio opportunità (se quote divergono)
- Diversificazione bookmaker (limite superato)

**File**: `scripts/multi_bookmaker.py` + nuova colonna dashboard

---

#### 9. **ML Continuo - Riaddestramento Settimanale** 🧠
**Cosa**: Cron job automatico riallena modelli ogni lunedì

```bash
# crontab
0 2 * * MON cd /path/to/pronostici && python scripts/modelli_predittivi.py
```

**Impatto**:
- Modello sempre aggiornato (ultimi risultati)
- Adattamento forma squadre (Pisa promosse, etc.)
- Zero manutenzione manuale

**File**: crontab + `scripts/auto_retrain.sh`

---

#### 10. **Backtesting Live - Alert Drift** 🚨
**Cosa**: Confronta predizioni vs risultati reali → alert se degrado

```python
def monitor_model_drift():
    """Monitora performance modello real-time"""
    df = pd.read_csv('tracking_giocate.csv')
    df_last_20 = df[df['Risultato'] != 'PENDING'].tail(20)
    
    roi_real = df_last_20['Profit'].sum() / len(df_last_20) * 100
    
    if roi_real < -5:
        send_alert("⚠️ ROI ultimi 20 bet: -5% → STOP BETTING!")
    elif roi_real < 0:
        send_alert("🟡 ROI in negativo, monitora")
```

**Impatto**:
- Protegge da losing streak (stop-loss automatico)
- Evidenzia model drift (riallena urgente)
- Risk management professionale

**File**: `scripts/monitor_drift.py` (esegui giornaliero)

---

## 🏆 Quick Wins da Implementare ORA (30 min)

### **A. Shrinkage Adattivo (implementazione minima)**

File: `web/app_professional.py` (dopo imports)

```python
def calcola_shrinkage_tracking():
    """Calcola shrinkage da tracking reale (se disponibile)"""
    try:
        df = pd.read_csv('tracking_giocate.csv')
        df_closed = df[df['Risultato'].isin(['WIN', 'LOSS'])]
        
        if len(df_closed) < 10:
            return 0.35  # Default
        
        # Estrai EV medio modello (rimuovi '%' e converti)
        ev_values = []
        for ev_str in df_closed['EV_Modello']:
            try:
                ev_num = float(str(ev_str).replace('+', '').replace('%', ''))
                ev_values.append(ev_num)
            except:
                pass
        
        if not ev_values:
            return 0.35
        
        ev_medio = sum(ev_values) / len(ev_values)
        roi_reale = (df_closed['Profit'].sum() / len(df_closed)) * 100
        
        shrinkage = max(0.15, min(0.50, roi_reale / ev_medio if ev_medio > 0 else 0.35))
        
        logger.info(f"📊 Shrinkage adattivo: EV modello {ev_medio:.1f}% → ROI reale {roi_reale:.1f}% = shrinkage {shrinkage:.2f}")
        
        return shrinkage
    except Exception as e:
        logger.warning(f"⚠️ Errore calcolo shrinkage adattivo: {e}")
        return 0.35  # Fallback conservativo
```

Poi modifica calcolo EV_Realistico (linea ~1750):

```python
# PRIMA (shrinkage fisso)
ev_realistico = ev_modello / 3.5

# DOPO (shrinkage adattivo)
shrinkage_factor = calcola_shrinkage_tracking()
ev_realistico = ev_modello * shrinkage_factor
```

**Risultato**: Dopo 10 bet, sistema auto-calibra EV basandosi su performance reale! 🎯

---

### **B. Pulsante "Suggerisci Stake Kelly" (30 min)**

File: `web/templates/diario_betting.html` (funzione editBet)

```javascript
function suggestKellyStake(bet) {
    // Kelly Criterion: (p*q - 1) / (q - 1)
    const probabilita = bet.prob_model / 100;  // Da 55% a 0.55
    const quota = parseFloat(bet.quota);
    const bankroll = 100;  // €100 default (user può cambiare)
    
    const b = quota - 1;
    const kelly = (probabilita * b - (1 - probabilita)) / b;
    const kelly_quarter = kelly * 0.25;  // 1/4 Kelly conservativo
    
    const stake_ottimale = Math.max(0, Math.min(bankroll * kelly_quarter, bankroll * 0.05));
    
    return stake_ottimale.toFixed(2);
}

// Modifica editBet per includere suggerimento
function editBet(bet) {
    const kellyStake = suggestKellyStake(bet);
    const nuovoStake = prompt(
        `💰 Modifica Stake:\n\n` +
        `Stake attuale: €${bet.stake}\n` +
        `📊 Kelly Criterion (1/4): €${kellyStake}\n\n` +
        `Inserisci nuovo stake:`,
        kellyStake  // Pre-compila con Kelly
    );
    // ...
}
```

**Risultato**: Ogni edit stake suggerisce automaticamente Kelly ottimale! 💰

---

## 📅 Timeline Suggerita

| Settimana | Obiettivo | Deliverable |
|-----------|-----------|-------------|
| **1** | Quick Wins | Shrinkage adattivo + Kelly stake |
| **2** | Analytics | Grafici equity + Export Excel |
| **3** | Notifiche | Telegram bot + Mobile responsive |
| **4** | Automazione | Scraping Sisal (fase 1) |
| **5-6** | Advanced | Multi-bookmaker + ML continuo |

---

## 🎯 Priorità Immediate (Max Impatto/Min Sforzo)

1. **Shrinkage Adattivo** (30 min) → EV più accurato automaticamente
2. **Kelly Stake** (30 min) → Bankroll management professionale
3. **Grafici Equity** (2h) → Visual feedback motivante
4. **Telegram Bot** (3h) → Zero opportunità perse

**Totale: ~6 ore per trasformare sistema in piattaforma pro-level** 🚀

---

## 💡 Note Implementazione

- **Testa locale PRIMA** di pushare su Render
- **Backup tracking_giocate.csv** prima di modifiche critiche
- **Shrinkage adattivo**: aspetta 20+ bet per stabilizzarsi
- **Kelly**: usa 1/4 o 1/8 Kelly (più conservativo = meno variance)
- **Telegram**: crea bot con @BotFather, API token gratis
- **Excel export**: usa openpyxl (già in requirements.txt)

---

**🎯 Prossimo Step**: Implementare Shrinkage Adattivo (30 min) → impatto immediato!
