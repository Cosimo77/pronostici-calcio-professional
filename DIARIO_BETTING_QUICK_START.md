# 📔 Diario Betting Professionale - Quick Start

Sistema completo di tracking puntate, analisi performance e validazione ROI reale.

## 🎯 Workflow Completo

### 1. Prima di Scommettere
```bash
# Controlla opportunità FASE2 (sweet spot 20-25% EV)
python3 run_professional_system.py

# Dashboard web (più user-friendly)
open http://localhost:5008/upcoming_matches
```

**Filtri validati:**
- EV: 20-25% (backtest ROI +24.55%)
- Mercati: DC_1X, DC_X2, UNDER_25
- ATTENZIONE: EV modello sovrastimato! Shrinkage ~70%

### 2. Aggiungi Puntata
```bash
python3 add_bet.py
```

**Input richiesti:**
- Partita: `Parma-Verona`
- Mercato: `1X`
- Quota Sisal: `1.45` (SEMPRE verifica su Sisal prima!)
- Stake €: `2.00`
- (Opzionali) EV modello, EV realistico, note

**Output:**
```
✅ Puntata salvata in tracking_giocate.csv
💡 Per vedere il diario: python3 betting_journal.py
```

### 3. Visualizza Diario
```bash
python3 betting_journal.py
```

**Statistiche mostrate:**
- 🎯 Puntate in attesa (PENDING)
- 📈 Performance storica (ROI, Win Rate, P/L)
- 🎲 Performance per mercato (1X, X2, UNDER, ecc.)
- 🔬 Calibrazione modello (EV previsto vs ROI reale)

**Opzioni:**
- Export diario (Excel/CSV) con timestamp
- Solo visualizzazione: `q` per uscire

### 4. Aggiorna Risultati (Post-Partita)
```bash
python3 update_bet.py
```

**Workflow:**
1. Mostra puntate in attesa
2. Scegli numero puntata da aggiornare
3. Seleziona risultato:
   - `1` = WIN 🏆 (calcola profit automaticamente)
   - `2` = LOSS ❌ (profit = -stake)
   - `3` = VOID (puntata annullata, stake restituito)
4. Conferma
5. Salvataggio automatico in CSV

**Esempio:**
```
[5] 15/02/2026 - Parma-Verona
    Mercato: 1X @ 1.45 | Stake: €2.00

Risultato:
  1. WIN 🏆
  2. LOSS ❌
  3. VOID

Seleziona (1/2/3): 1

✅ VITTORIA!
   Profit: €+0.90

💾 Risultato salvato!
```

### 5. Analisi Performance (Vecchio Script)
```bash
python3 analizza_tracking.py
```

**Output:**
- Lista puntate attive
- Statistiche completate (ROI, WR, P/L)
- Confronto EV modello vs reale

---

## 📊 Struttura Dati (tracking_giocate.csv)

```csv
Data,Partita,Mercato,Quota_Sistema,Quota_Sisal,EV_Modello,EV_Realistico,Stake,Risultato,Profit,Note
15/02/2026,Parma-Verona,1X,1.45,1.45,+23.3%,+3%,2.00,PENDING,0.00,Parma casa solida
```

**Campi critici:**
- `Quota_Sisal`: Quota REALE (verifica manualmente!)
- `EV_Realistico`: EV corretto dopo shrinkage (~30% EV modello)
- `Risultato`: PENDING / WIN / LOSS / VOID
- `Profit`: Calcolato automaticamente da `update_bet.py`

---

## 💡 Best Practices

### ✅ DO (Consigliato)
1. **Verifica SEMPRE quota su Sisal** prima di bet
2. **Applica shrinkage 70%** a EV modello (es. +22% → +7% reale)
3. **Stake conservativo**: 1-2% bankroll (€2-5 per bankroll €100-250)
4. **Minimo 20 puntate** prima validare ROI reale
5. **Smetti se ROI <0%** dopo 30+ bet (modello non funziona)
6. **Tracking rigoroso**: aggiorna risultati entro 24h partita

### ❌ DON'T (Evita)
1. NO puntate con EV >25% (backtest ROI -29%, troppa variance)
2. NO puntate automatiche senza verifica quote Sisal
3. NO aumenti stake dopo loss (no martingala)
4. NO fiducia cieca in EV modello (è sovrastimato!)
5. NO skip tracking puntate (fondamentale per validazione)

---

## 🔬 Validazione ROI Reale

### Target Realistici
- **ROI modello backtest**: +21.8% (DC), +7.2% (Pareggi)
- **ROI reale atteso**: +3-8% (dopo shrinkage EV)
- **Win Rate atteso**: 55-65% (DC), 30-35% (Pareggi/UNDER)

### Milestone
- **10 bet**: Troppo presto (variance alta)
- **20 bet**: Primo check (se ROI <-10% considera stop)
- **50 bet**: Validazione statistica significativa
- **100+ bet**: Confidenza ROI long-term

### Esempio Calcolo
```python
# Dopo 20 puntate
Stake totale: €40.00
Profit netto: €+2.80
ROI reale: +7.0%

EV medio modello: +22.5%
Shrinkage factor: 7.0 / 22.5 = 0.31x (31%)
```

Se shrinkage <20%: Modello troppo ottimista, rivaluta filtri

---

## 🛠️ Risoluzione Problemi

### Diario non mostra puntate
```bash
# Verifica CSV esiste
ls -lh tracking_giocate.csv

# Se mancante, crea prima puntata
python3 add_bet.py
```

### Errore "NaN" su stake
- Causa: Stake = "MONITOR" in CSV (non numerico)
- Fix: Edita CSV manualmente o cancella riga

### Quote diverse da dashboard
- Dashboard mostra **The Odds API** (aggiornate ogni 15min)
- **USA SEMPRE quote Sisal** (verificate manualmente prima bet)
- Dashboard = screening, Sisal = verità

### ROI reale negativo dopo 20 bet
1. Verifica errori tracking (risultati corretti?)
2. Calcola shrinkage EV (se <20%, modello unreliable)
3. Considera **STOP** betting se ROI <-15%
4. Option: Riaddestra modello con più dati recenti

---

## 📈 Prossimi Step (Dopo 20+ Puntate)

1. **Analisi statistica avanzata**:
   ```bash
   python3 analizza_tracking_fase1.py  # Confidence intervals, Kelly criterion
   ```

2. **Re-calibrazione filtri**:
   - Se ROI reale <0%: Aumenta threshold EV (25-30%)
   - Se ROI reale >10%: Cautamente allenta (15-25%)

3. **Backtest validation**:
   ```bash
   python3 backtest_fase2_completo.py --validation-split
   # Train/test temporale per evitare overfitting
   ```

4. **Automazione avanzata**:
   - Scraping Sisal automatico (quote reali)
   - Notifiche push nuove opportunità
   - Dashboard mobile-friendly

---

## 📚 Documenti di Riferimento

- [FASE2_CALIBRATA_PROFESSIONISTI.md](FASE2_CALIBRATA_PROFESSIONISTI.md) - Backtest e sweet spot
- [GUIDA_OPERATIVA_FASE1.md](GUIDA_OPERATIVA_FASE1.md) - Filtri pareggi (ROI +7.2%)
- [README.md](README.md) - Setup sistema generale

---

## ⚠️ Disclaimer

Il sistema **NON garantisce profitto**. ROI +21.8% è backtest su dati storici, **non performance futura**.

**EV modello è sovrastimato** (~70% shrinkage). User verifica dato confronto Sisal:
- EV modello: +22-28%
- EV reale: +3-8%

Usa sistema come **screening intelligente**, non oracolo. Validazione critica quote + tracking rigoroso = fondamentali.

**Scommetti solo ciò che puoi permetterti di perdere.**
