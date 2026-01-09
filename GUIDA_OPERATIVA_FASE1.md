# 🎯 GUIDA OPERATIVA FASE1 - GENNAIO 2026

## Sistema Profittevole Validato
- **ROI Backtest**: +7.17% (510 trade storici)
- **Win Rate**: 31.0%
- **Max Drawdown**: -52.3%
- **Strategia**: Pareggi selettivi quote 2.8-3.5, EV 25-50%

---

## 📅 WORKFLOW SETTIMANALE

### Lunedì/Martedì - Identificazione Opportunità

1. **Vai su bookmaker** (Bet365, Snai, Eurobet)
2. **Copia quote** prossime partite Serie A (weekend)
3. **Modifica** `valida_fase1_realtime.py` linea 245:

```python
partite_prossime = [
    ('Juventus', 'Milan', {'H': 2.10, 'X': 3.20, 'A': 3.50}),
    ('Inter', 'Napoli', {'H': 2.05, 'X': 3.40, 'A': 3.80}),
    # ... aggiungi tutte le partite weekend
]
```

4. **Esegui analisi**:
```bash
python3 valida_fase1_realtime.py
```

5. **Annota opportunità** che passano filtri FASE1

---

### Sabato/Domenica - Piazzamento Trade (Paper Trading)

**PER OGNI opportunità identificata:**

1. **Verifica quote live** 30min prima partita (possono cambiare!)
2. **Ricalcola EV** con quota aggiornata
3. **Se ancora valida FASE1**: annota nel tracking

**Apri** `tracking_fase1_gennaio2026.csv` e aggiungi riga:

```
11/01/2026,20,Juventus,Milan,3.20,42.5,0.41,X,PENDING,€48.00,0,€500.00,0,
```

Campi:
- Data partita
- Giornata Serie A
- Casa, Ospite
- Quota X aggiornata
- EV %
- Confidenza modello
- Predizione (sempre X per FASE1)
- Risultato: PENDING (cambierai dopo)
- Stake: calcola come €500 × 0.387 × 0.25 = €48
- Profit/Loss: 0 (per ora)
- Bankroll: attuale
- ROI: 0
- Note: eventuali (es. "Quota calata da 3.30")

4. **ZERO soldi reali** ancora! Solo annotazione

---

### Lunedì Successivo - Aggiornamento Risultati

1. **Controlla risultati** partite weekend
2. **Aggiorna CSV** per ogni trade:

**Se pareggio (WIN):**
```
Risultato: X
Profit_Loss: €105.60  (= €48 × 3.20 - €48)
Bankroll: €605.60
ROI_%: +21.12
```

**Se non pareggio (LOSS):**
```
Risultato: H  (o A)
Profit_Loss: -€48.00
Bankroll: €452.00
ROI_%: -9.60
```

3. **Analizza performance**:
```bash
python3 analizza_tracking_fase1.py
```

4. **Decision check** (dopo 20+ trade):
   - ROI >+3%: ✅ Considera deploy reale
   - ROI 0-3%: ⚠️ Continua paper trading
   - ROI <0%: ❌ Rivedi filtri

---

## 🛡️ REGOLE FERREE

### Durante Paper Trading
- ✅ Max 2 trade/giorno
- ✅ Skip se quota cambia >0.2 (es. 3.20→3.00)
- ✅ Skip se EV scende <25%
- ❌ NO revenge betting dopo loss
- ❌ NO deviazione criteri FASE1

### Stop Loss Automatici
- **3 loss consecutive**: pausa 1 settimana
- **Drawdown >60%**: STOP totale, rivedi sistema
- **ROI <-15% dopo 30 trade**: pausa 2 settimane

---

## 📊 CHECKPOINT DECISION

### Dopo 20 Trade
```
SE win_rate ≥28% AND roi >+3%:
  → Procedi FASE 3 (deploy €250)
  
SE win_rate 25-28% AND roi 0-3%:
  → Continua paper trading 10 trade
  
SE win_rate <25% OR roi <0%:
  → STOP, analizza dati, rivedi filtri
```

### Dopo 50 Trade
```
SE roi >+5% consistente:
  → Scale a €500 bankroll reale
  → Inizia strategie complementari (Home, DC)
  
SE roi +3-5%:
  → Mantieni €250, monitora variance
  
SE roi <+3%:
  → Back to drawing board
```

---

## 💰 QUANDO PASSARE A SOLDI REALI

**Requisiti MINIMI:**
1. ✅ 20+ trade paper trading completati
2. ✅ ROI >+3%
3. ✅ Win rate ≥28%
4. ✅ Max drawdown <60%
5. ✅ Comprensione piena sistema
6. ✅ Disciplina emotiva testata

**Start Conservativo:**
- Bankroll: €250 (NON €500!)
- Stake: €12-15 per trade
- Target mensile: +€10-20 (4-8%)

**Scaling Progressivo:**
- Mese 1: €250
- Mese 2: €500 (se ROI >+5%)
- Mese 3: €1,000 (se ROI consistente)

---

## 🚨 RED FLAGS - STOP IMMEDIATO

### Durante Paper Trading
- Drawdown >70%
- 5+ loss consecutive
- Win rate <20% su 30+ trade
- Stress emotivo durante tracking

### Durante Deploy Reale
- QUALSIASI punto sopra
- Tentazione aumentare stake post-loss
- Skippare regole "solo questa volta"
- Impatto negativo su vita/sonno

---

## 📞 SUPPORTO

### Script Disponibili
```bash
# Identifica opportunità prossimo weekend
python3 valida_fase1_realtime.py

# Analizza performance tracciata
python3 analizza_tracking_fase1.py

# Backtest su nuovi dati
python3 backtest_fase1_improved.py
```

### File Tracking
- `tracking_fase1_gennaio2026.csv`: CSV principale
- Backup manuale settimanale consigliato

---

## 🎯 OBIETTIVI GENNAIO 2026

**Week 1-2:**
- [ ] Identificare 5-10 opportunità FASE1
- [ ] Completare primi 10 trade paper
- [ ] Familiarizzare con workflow

**Week 3-4:**
- [ ] Raggiungere 20 trade totali
- [ ] Primo checkpoint decision
- [ ] Validare ROI >+3%

**Fine Gennaio:**
- [ ] 25-30 trade completati
- [ ] Decision FASE 3 (deploy reale)
- [ ] Setup bankroll reale se validato

---

## 💡 RICORDA

> "Il betting profittevole è 90% disciplina, 10% matematica."

- **NON** cercare trade forzati
- **NON** deviare dai criteri
- **SÌ** alla pazienza
- **SÌ** al tracking rigoroso

La FASE1 ha fatto +7.17% su 510 trade storici.  
Ora devi solo **validare che funziona ancora** su dati fresh.

---

📅 **Prossima azione**: Identifica partite questo weekend e aggiungi a `valida_fase1_realtime.py`

🎯 **Goal immediato**: 10 trade paper tracking entro 20 Gennaio

✅ **Success metric**: ROI >+3% dopo 20 trade
