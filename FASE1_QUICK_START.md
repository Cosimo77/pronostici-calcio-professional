# ⚡ FASE1 - Quick Start Guide

**Sistema 100% Automatico** - Zero configurazione richiesta

---

## 🚀 Uso Immediato (One-Click)

### Scansione Settimanale

```bash
# Ogni lunedì mattina (10 minuti)
./run_fase1_auto.sh
```

Fa TUTTO automaticamente:
- ✅ Scarica quote da The Odds API
- ✅ Identifica opportunità FASE1
- ✅ Salva nel tracking CSV
- ✅ Aggiorna risultati partite passate
- ✅ Genera report performance

---

## 📊 Risultati Prima Settimana

**Data**: 7 Gennaio 2026  
**Partite analizzate**: 17  
**Opportunità FASE1**: 10  
**API requests usati**: 9/500 (rimangono 491)

### Opportunità Trovate

| Data | Partita | Quota | EV | Stake |
|------|---------|-------|-----|-------|
| 07/01 | Bologna-Atalanta | 3.25 | +37.5% | €48.38 |
| 07/01 | Lazio-Fiorentina | 3.00 | +26.7% | €48.38 |
| 07/01 | Torino-Udinese | 3.01 | +27.3% | €48.38 |
| 08/01 | Cremonese-Cagliari | 3.07 | +30.0% | €48.38 |
| 10/01 | Como-Bologna | 3.26 | +37.9% | €48.38 |
| 10/01 | Udinese-Pisa | 3.24 | +37.2% | €48.38 |
| 11/01 | Lecce-Parma | 2.96 | +25.1% | €48.38 |
| 11/01 | **Fiorentina-Milan** | 3.46 | **+46.5%** | €48.38 |
| 11/01 | Verona-Lazio | 3.08 | +30.1% | €48.38 |
| 12/01 | Genoa-Cagliari | 2.97 | +25.8% | €48.38 |

**Statistiche**:
- EV medio: +32.4%
- Quote range: 2.96-3.46 ✅ (tutte in 2.8-3.5)
- Stake totale: €483.80
- Bankroll: €500

---

## 📖 Comandi Manuali (Opzionali)

Se preferisci controllo manuale:

```bash
python3 fase1_automatico.py
```

**Menu**:
1. 🔍 **SCAN** - Identifica opportunità
2. 🔄 **UPDATE** - Aggiorna risultati
3. 📊 **REPORT** - Mostra performance
4. 🚀 **AUTO** - Tutto in uno (consigliato)

---

## 📅 Workflow Settimanale

### Lunedì (10:00)
```bash
./run_fase1_auto.sh
```
→ Identifica opportunità per il weekend

### Dopo Partite (Domenica sera/Lunedì)
```bash
./run_fase1_auto.sh
```
→ Aggiorna automaticamente risultati dal dataset

### Fine Mese
```bash
python3 fase1_automatico.py → Opzione 3 (REPORT)
```
→ Report completo con decisione (continua/scala/stop)

---

## 🎯 Target Performance (Paper Trading)

**Minimo 20 trade** prima di decidere:

| Metrica | Target | Azione |
|---------|--------|--------|
| ROI | ≥+3% | ✅ Passa a deploy reale (€250) |
| ROI | 0-3% | ⚠️ Continua paper trading +10 trade |
| ROI | <0% | ❌ Stop e rivedi strategia |
| Win Rate | ≥28% | ✅ Sistema funzionante |
| Max Drawdown | <60% | ✅ Rischio controllato |

**FASE1 Validato**: ROI +7.17% su 510 trade storici

---

## ⚠️ Stop Loss Automatici

Il sistema si ferma SE:
- Drawdown >70% (limite sicurezza)
- 5 perdite consecutive
- ROI <-10% dopo 30 trade

---

## 🔄 Automazione Completa (Cron)

### Setup Una Tantum

```bash
crontab -e
```

Aggiungi:
```cron
# FASE1 automatico ogni lunedì ore 10:00
0 10 * * 1 /Users/cosimomassaro/Desktop/pronostici_calcio/run_fase1_auto.sh >> ~/fase1.log 2>&1
```

Salva e esci. **Sistema completamente autonomo**.

---

## 📊 Monitoring Oggi

```bash
./monitora_oggi.sh
```

Mostra partite di OGGI con quote/stake.

---

## 💡 Pro Tips

1. **API Quota Management**: 500 richieste/mese
   - 1 scan = ~8-10 richieste
   - Massimo 2 scan/settimana = 80 req/mese
   - Margine: 420 richieste spare

2. **Kelly Conservativo**: Stake 0.25× Kelly
   - €48.38 per trade (~10% bankroll)
   - Rischio controllato
   - Crescita sostenibile

3. **Paper Trading Disciplina**:
   - NO soldi reali fino a 20+ trade validati
   - Tracking rigoroso CSV
   - Decisione basata su dati, non emozioni

---

## 📞 Troubleshooting

**Q: Non trova opportunità?**  
A: Normale! Filtri FASE1 molto selettivi (quote 2.8-3.5, EV 25-50%). Alcune settimane 0 opportunità.

**Q: API quota esaurita?**  
A: Riduci scansioni a 1/settimana o aspetta prossimo mese (reset automatico).

**Q: Risultati non aggiornati?**  
A: Dataset si aggiorna con `aggiorna_rapido.py`. UPDATE automatico cerca match nel dataset esistente.

---

## 🎉 Next Steps

1. ✅ Monitora partite 7-12 gennaio
2. ✅ Dopo domenica: UPDATE automatico
3. ✅ Valuta performance dopo 20 trade
4. ✅ Setup cron per automazione totale

**Il sistema è PRONTO. Segui la strategia con disciplina!** 🚀
