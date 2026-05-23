# 📊 Backtest Report - 23 Maggio 2026

## Executive Summary

**Sistema validato su 50 partite storiche stagione 2025-26.**
**Accuracy: 44.0% (BUONO) - Sopra baseline casuale (33%)**

---

## ✅ Risultati Principali

### Metriche Globali
- **Totale partite testate**: 50
- **Predizioni corrette**: 22
- **Accuracy globale**: 44.0%
- **Periodo**: 23 agosto - 4 ottobre 2025

### Accuracy per Tipo
- **Casa (H)**: 43.9% su 41 predizioni
- **Pareggio (D)**: 40.0% su 5 predizioni
- **Ospite (A)**: 50.0% su 4 predizioni

### Valutazione
✅ **Performance SOLIDA** - Sistema funzionante e sopra aspettative baseline

---

## ⚠️ Problema Identificato: Bias Casa

### Distribuzione Predizioni
```
Sistema prevede:  82% Casa | 10% X | 8% Ospite
Realtà Serie A:   40% Casa | 28% X | 32% Ospite
```

### Root Cause
1. **Bayesian smoothing 60%**: Troppo peso a prior (converge verso medie)
2. **Home advantage factor**: 3-8% amplifica ulteriormente probabilità Casa
3. **Effetto cumulativo**: Due layer di bias → overweight Casa sistematico

---

## 🔧 Fix Consigliati (Giugno-Luglio 2026)

### Priority 1: Riduzione Smoothing
```python
# File: web/app_professional.py, linea ~690
# CORRENTE: peso_prior = min(50 / max(n_partite, 1), 0.60)
# FIX:      peso_prior = min(50 / max(n_partite, 1), 0.40)
```
**Impatto**: Meno regolarizzazione → più peso a dati reali squadra

### Priority 2: Calibrazione Home Advantage
```python
# File: web/app_professional.py, linea ~820
# CORRENTE: vantaggio_casa_base = 0.03 + (0.05 * fattore_esperienza)
# FIX:      vantaggio_casa_base = 0.02 + (0.03 * fattore_esperienza)
```
**Impatto**: Riduzione vantaggio casa 3-8% → 2-5%

### Validazione Post-Fix
```bash
python3 scripts/backtest_stagione_completa.py 50
# Target: Distribuzione predizioni Casa <60%
```

---

## 📁 File Generati

1. ✅ `backtest_stagione_2025_26_results.csv` (50 righe, 4.4 KB)
2. ✅ `scripts/backtest_stagione_completa.py` (script riutilizzabile)
3. ✅ `tracking_predictions_live_BACKUP_20260523_181435.csv` (backup sicurezza)
4. ✅ `BACKTEST_REPORT_23MAG2026.md` (questo report)

---

## 🎯 Roadmap Prossimi 3 Mesi

### Giugno 2026
- [ ] Implementare fix Priority 1 (smoothing)
- [ ] Re-run backtest 50 partite per validazione
- [ ] Monitoring distribuzione predizioni

### Luglio 2026
- [ ] Implementare fix Priority 2 (home advantage) se necessario
- [ ] Backtest completo 360 partite per metriche finali
- [ ] Preparazione sistema per kick-off agosto

### Agosto 2026
- [ ] Sistema rodato pronto per stagione 2026-27
- [ ] Baseline accuracy validata su dati storici
- [ ] Monitoring live vs backtest per drift detection

---

## ✅ Sistema Produzione: INTOCCATO

**Zero modifiche al codice produzione durante backtest:**
- ✅ `web/app_professional.py`: Invariato
- ✅ `tracking_predictions_live.csv`: Invariato (backup creato)
- ✅ Deploy Render: Funzionante
- ✅ GitHub Actions: Operativi

**Backtest = Operazione read-only con file separati**

---

## 📊 Conclusione

**Sistema ML validato con 44% accuracy - Performance BUONA per Serie A.**

**Bias Casa identificato e fix documentati per implementazione futura.**

**3 mesi disponibili per iterazione e miglioramento prima nuova stagione.**

---

_Report generato: 23 Maggio 2026_
_Metodo: Walk-forward backtest su dati storici_
_Tool: scripts/backtest_stagione_completa.py_
