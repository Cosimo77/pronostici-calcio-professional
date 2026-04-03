# ⚽ Sistema Pronostici Calcio Professional

[![Tests & Coverage](https://github.com/Cosimo77/pronostici-calcio-professional/actions/workflows/test.yml/badge.svg)](https://github.com/Cosimo77/pronostici-calcio-professional/actions/workflows/test.yml)
[![Deploy Validation](https://github.com/Cosimo77/pronostici-calcio-professional/actions/workflows/deploy-validate.yml/badge.svg)](https://github.com/Cosimo77/pronostici-calcio-professional/actions/workflows/deploy-validate.yml)
[![codecov](https://codecov.io/gh/Cosimo77/pronostici-calcio-professional/branch/main/graph/badge.svg)](https://codecov.io/gh/Cosimo77/pronostici-calcio-professional)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Production Status](https://img.shields.io/badge/production-healthy-success)](https://pronostici-calcio-professional.onrender.com)

Sistema avanzato e completamente automatizzato per l'analisi e previsione dei risultati calcistici utilizzando machine learning, automazione intelligente e monitoraggio in tempo reale.

**Rating Sistema**: ⭐⭐⭐⭐⭐ **9.2/10** (Production-Ready + CI/CD)
**Last Update**: 3 Aprile 2026 - [Tier 3 CI/CD Pipeline](docs/deployment/BRANCH_PROTECTION.md) implementato

## 📚 Documentazione

Per documentazione completa e guide operative, vedi [docs/README.md](docs/README.md):
- 📦 **Deployment**: Setup Render, configuration produzione
- 📖 **Guide Operative**: Quick start FASE 1, workflow trading
- ✅ **Certificazioni**: Validazioni sistema, dati reali, dual strategy
- 📝 **Changelog**: Miglioramenti, bug fix, feature release

## 🚀 Avvio Rapido

### Installazione

```bash
# Setup completo del sistema
python launcher.py --setup

# Clone repository

git clone <<<<<https://github.com/Cosimo77/pronostici-calcio-professional.git#>>>>> Avvio sistema completo

cd pronostici-calcio-professionalpython launcher.py



# Installa dipendenze# Oppure avvia servizi singoli

pip install -r requirements.txtpython launcher.py --service web

python launcher.py --service monitoring

# Avvia sistemapython launcher.py --service automation

python automation_master.py  # Daemon automazione```

python -m web.app_professional  # Web server

```Accedi all'applicazione:



### Accesso Dashboard- **App Principale**: <<<<<<http://localhost:5000>>>>>>

- **Dashboard Monitoraggio**: <<<<<<http://localhost:5001>>>>>>

- **Web App**: <<<<<<http://localhost:5008>>>>>>

- **Monitoring**: <<<<<<http://localhost:5008/monitoring>##>>>>> ✨ Caratteristiche Principali

- **Automazione**: <<<<<<http://localhost:5008/automation>>>>>>

- **Produzione**: <<<<<<https://pronostici-calcio-professional.onrender.com>###>>>>> 🎯 Core Features



## 📊 Funzionalità- **14 Mercati di Scommesse**: 1X2, Over/Under, Goal/NoGoal, Asian Handicap, ecc.

- **Machine Learning Avanzato**: Random Forest, Gradient Boosting, Logistic Regression

### Predizioni ML- **Interface Web Responsive**: Dashboard moderna con grafici interattivi

- **API RESTful Completa**: Endpoint per tutti i mercati e analisi

- **3 Modelli**: RandomForest, GradientBoosting, LogisticRegression

- **Mercati**: 1X2, Over/Under, GG/NG, Doppia Chance### 🤖 Automazione Intelligente

- **Ensemble**: Combinazione modelli con voting

- **Confidenza**: Score 0-100% per ogni predizione- **Aggiornamento Automatico**: Dati aggiornati quotidianamente da fonti multiple

- **Riaddestramento Modelli**: Modelli ML riaddestrati settimanalmente

### Automazione- **Backup Automatici**: Backup incrementali di dati e modelli

- **Health Checks**: Monitoraggio continuo dello stato del sistema

- ✅ **Aggiornamento dati**: Quotidiano ore 06:00

- ✅ **Training modelli**: Domenica ore 02:00### 📊 Monitoraggio e Analytics

- ✅ **Backup automatici**: Dopo ogni operazione

- ✅ **Health check**: Ogni ora- **Dashboard Real-time**: Stato sistema, accuratezza predizioni, performance

- **Log Centralizzati**: Logging strutturato di tutte le operazioni

### Dashboard- **Metriche Avanzate**: Tracking accuratezza, tempi di risposta, errori

- **Alerting**: Notifiche automatiche per anomalie

- **Enterprise**: Interface completa predizioni

- **Monitoring**: Metriche sistema real-time## 🏗️ Struttura del Progetto

- **Automation**: Stato automazione e timestamp

```text

## 🏗️ Architetturapronostici_calcio/

├── data/                          # Dati storici e processati

### Sistema Ibrido (Locale + Cloud)│   ├── I1_2021.csv               # Dati Serie A 2020-21

│   ├── I1_2122.csv               # Dati Serie A 2021-22

```text│   ├── I1_2223.csv               # Dati Serie A 2022-23

┌─────────────────────────────────────────┐│   ├── I1_2324.csv               # Dati Serie A 2023-24

│  MAC (Locale)                           ││   ├── I1_2425.csv               # Dati Serie A 2024-25

│  ├─ automation_master.py (daemon)       ││   ├── I1_2526.csv               # Dati Serie A 2025-26

│  ├─ Aggiornamento dati: 06:00 daily     ││   ├── I1_2526.csv               # Dati Serie A 2025-26

│  ├─ Training modelli: 02:00 domenica    ││   ├── dataset_pulito.csv        # Dataset unificato e pulito

│  └─ Backup: automatico                  ││   └── dataset_features.csv      # Dataset con features engineered

└─────────────────────────────────────────┘├── models/                        # Modelli addestrati

                    ↓ git push│   ├── randomforest_model.pkl

┌─────────────────────────────────────────┐│   ├── gradientboosting_model.pkl

│  GITHUB                                 ││   ├── logisticregression_model.pkl

│  └─ Codice + Dati + Modelli             ││   ├── scaler.pkl

└─────────────────────────────────────────┘│   └── metadata.pkl

                    ↓ auto-deploy├── scripts/                       # Script Python

┌─────────────────────────────────────────┐│   ├── scarica_dati_storici.py   # Download dati da football-data.co.uk

│  RENDER (Cloud)                         ││   ├── analizza_dati.py          # Analisi esplorativa

│  ├─ app_professional.py (web server)    ││   ├── feature_engineering.py    # Creazione features

│  └─ Dashboard 24/7                      ││   ├── modelli_predittivi.py     # Training modelli ML

└─────────────────────────────────────────┘│   └── sistema_pronostici.py     # Interfaccia utente

```├── main.py                        # Script principale

└── README.md                      # Questo file

## 📁 Struttura Progetto```



```text## 🚀 Installazione e Setup

pronostici_calcio/

├── web/                      # Web application### 1. Prerequisiti

│   ├── app_professional.py   # Main Flask app

│   ├── templates/            # HTML templates```bash

│   └── static/               # CSS/JS assets# Python 3.8+

├── scripts/                  # ML scriptspython3 --version

│   ├── analizza_dati.py      # Data analysis

│   ├── feature_engineering.py# Installa le dipendenze

│   └── mercati_multipli.py   # Market predictionspip install pandas numpy scikit-learn matplotlib seaborn requests joblib

├── data/                     # Datasets```

│   ├── dataset_pulito.csv    # Clean dataset

│   └── I1_*.csv              # Historical data### 2. Setup Automatico

├── models/                   # Trained models

│   └── enterprise/           # Production models```bash

├── logs/                     # System logs# Esegui lo script principale

│   └── automation_status.jsonpython3 main.py

└── automation_master.py      # Automation daemon

```# Seleziona l'opzione 1 per il setup completo

```

## 🔧 Configurazione

### 3. Setup Manuale (step-by-step)

### Environment Variables

```bash

```bash# 1. Scarica dati storici

# Web Serverpython3 scripts/scarica_dati_storici.py

PORT=5008

FLASK_ENV=production# 2. Analisi esplorativa

python3 scripts/analizza_dati.py

# Data Sources

FOOTBALL_DATA_URL=<<<<<https://www.football-data.co.uk#>>>>> 3. Feature engineering

```python3 scripts/feature_engineering.py



### Automazione# 4. Training modelli

python3 scripts/modelli_predittivi.py

File: `config/automation_config.json`

# 5. Avvia sistema pronostici

```jsonpython3 scripts/sistema_pronostici.py

{```

  "daily_update": "06:00",

  "weekly_retrain": "Sunday 02:00",## 🎯 Utilizzo

  "backup_rotation": 3,

  "health_check": "hourly"### Menu Principale

}

```Il sistema offre diverse opzioni:



## 📈 Performance Modelli1. **🔮 Predici una partita** - Predizione interattiva

2. **🏟️ Mostra squadre** - Lista squadre disponibili

Dataset: 1990 partite (2020-2025)3. **📈 Analizza forma** - Analisi forma recente squadre

4. **❌ Esci** - Chiude il sistema

| Modello | Accuracy | Precision | Recall |

| --------- | ---------- | ----------- | -------- |### Esempio di Predizione

| RandomForest | 50.1% | 48.2% | 51.3% |

| GradientBoosting | 52.6% | 50.8% | 53.1% |```text

| LogisticRegression | 56.5% | 54.2% | 57.8% |🔮 PREDIZIONE PARTITA



## 🛠️ TecnologieSeleziona la squadra di CASA:

1. Atalanta

- **Backend**: Python 3.11, Flask 3.1.02. Bologna

- **ML**: scikit-learn, pandas, numpy...

- **Frontend**: HTML5, CSS3, Vanilla JavaScript20. Juventus

- **Deploy**: Render.com (Free Tier)...

- **Automation**: schedule library, daemon process

- **Security**: Flask-Talisman, rate limitingInserisci il numero della squadra di casa: 20



## 📝 API EndpointsSeleziona la squadra in TRASFERTA:

1. Atalanta

### Predizioni...

13. Inter

```bash...

# Predizione Enterprise

POST /api/predict_enterpriseInserisci il numero della squadra in trasferta: 13

{

  "squadra_casa": "Juventus",⚽ PARTITA: Juventus vs Inter

  "squadra_ospite": "Milan"🤖 Calcolo predizione in corso...

}

🎯 PREDIZIONE: Vittoria Juventus

# Health Check🎲 Confidenza: 67.5%

GET /api/health

📊 PROBABILITÀ DETTAGLIATE:

# Performance Modelli   Casa: 67.5%

GET /api/model_performance   Trasferta: 20.1%

```   Pareggio: 12.4%



## 🤝 Contribuire💡 CONSIGLI SCOMMESSE:

🟢 ALTA CONFIDENZA - Consigliato scommettere

1. Fork il progetto⚽ SUGGERIMENTO: Possibile Over 2.5 gol

2. Crea branch (`git checkout -b feature/AmazingFeature`)```

3. Commit (`git commit -m 'Add AmazingFeature'`)

4. Push (`git push origin feature/AmazingFeature`)## 📊 Features Utilizzate

5. Apri Pull Request

Il sistema utilizza oltre 30 features per ogni predizione:

## 📄 Licenza

### Features di Forma

Questo progetto è privato. Tutti i diritti riservati.

- Media punti ultime 5 partite

## 👤 Autore- Gol fatti/subiti ultime 5 partite

- Performance specifica casa/trasferta

**Cosimo Massaro**

### Features Comparative

- GitHub: [@Cosimo77](https://github.com/Cosimo77)

- Progetto: [pronostici-calcio-professional](https://github.com/Cosimo77/pronostici-calcio-professional)- Differenza di forma tra le squadre

- Differenza attacco vs difesa

## 🙏 Ringraziamenti- Performance head-to-head storica



- [football-data.co.uk](https://www.football-data.co.uk) - Dati storici Serie A### Features Derivate

- [scikit-learn](https://scikit-learn.org) - Machine Learning

- [Flask](https://flask.palletsprojects.com) - Web Framework- Rapporto casa-home vs trasferta-away

- [Render](https://render.com) - Cloud Hosting- Trend di performance recente

- Statistiche scontri diretti

---

## 🤖 Modelli Utilizzati

*Sistema Professional v2.0 - Aggiornato il 2 Novembre 2025*

### 1. Random Forest

- **Accuracy**: ~50%
- **Parametri**: 200 estimatori, profondità illimitata
- **Punti di forza**: Gestione overfitting, feature importance

### 2. Gradient Boosting

- **Accuracy**: ~50%
- **Parametri**: Learning rate 0.05, profondità 3
- **Punti di forza**: Sequenziale, migliora errori precedenti

### 3. Logistic Regression

- **Accuracy**: ~52%
- **Parametri**: Regolarizzazione L1, C=0.1
- **Punti di forza**: Veloce, interpretabile

### 4. Ensemble

- **Accuracy**: ~50%
- **Metodo**: Voto pesato per accuracy individuale
- **Vantaggio**: Combina punti di forza di tutti i modelli

## 📈 Performance del Sistema

### Metriche di Valutazione

```text

Accuratezza Generale: ~50%
Precisione per Classe:

- Vittoria Casa: 53%
- Vittoria Trasferta: 52%
- Pareggio: 24%

Cross-Validation: 50.8% (±5.3%)

```

### Interpretazione

- **50% accuracy** è un risultato eccellente per predizioni calcistiche
- Il calcio ha un alto grado di casualità intrinseca
- Performance superiori al caso (33.3%) e alle quote bookmaker (~45%)
- Particolare difficoltà nel predire i pareggi (comune nei sistemi di ML calcistici)

## 📊 Analisi Dati

### Dataset

- **1,940 partite** analizzate (2020-2025)
- **29 squadre** diverse
- **162 colonne** originali dai dati
- **32 features** engineered finali

### Distribuzione Risultati

- Vittorie Casa: 40.7%
- Vittorie Trasferta: 32.2%
- Pareggi: 27.1%

### Statistiche Gol

- Media gol casa: 1.46
- Media gol trasferta: 1.26
- Media gol totali: 2.72
- Over 2.5: 50.8%

## 🔧 Personalizzazione

### Aggiunta Nuove Features

Modifica `feature_engineering.py` per aggiungere nuove features:

```python

# Esempio: Feature meteo
def calcola_feature_meteo(self, data_partita):
    # La tua implementazione
    return meteo_score

# Aggiungi alla funzione crea_features()
feature_dict['meteo_score'] = self.calcola_feature_meteo(data_partita)

```

### Nuovi Modelli

Aggiungi nuovi modelli in `modelli_predittivi.py`:

```python

'XGBoost': {
    'model': XGBClassifier(random_state=random_state),
    'params': {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1]
    },
    'use_scaling': False
}

```

## 🔄 Aggiornamento Dati

### Automatico

```bash

python3 main.py
# Seleziona opzione 2: "Solo scarica dati aggiornati"

```

### Manuale

```bash

python3 scripts/scarica_dati_storici.py
python3 scripts/analizza_dati.py
python3 scripts/feature_engineering.py
python3 scripts/modelli_predittivi.py

```

## ⚠️ Limitazioni e Disclaimer

### Limitazioni Tecniche

- Predizione pareggi limitata (comune problema ML calcistico)
- Dipendenza da dati storici (squadre neo-promosse)
- Non considera: infortuni, squalifiche, meteo, motivazioni

### Disclaimer Importante

⚠️ **QUESTO SISTEMA È SOLO A SCOPO EDUCATIVO E DI RICERCA**

- Non garantisce profitti nelle scommesse
- Il calcio ha alta componente di casualità
- Scommettere comporta sempre rischi finanziari
- Usare sempre con responsabilità e moderazione

## 🤝 Contributi

Il progetto è aperto a contributi! Aree di miglioramento:

1. **Nuove Features**: Meteo, infortuni, forma fisica
2. **Modelli Avanzati**: Neural Networks, XGBoost
3. **Interfaccia Web**: Dashboard con Flask/Django
4. **API Integration**: Dati live, quote bookmaker
5. **Visualizzazioni**: Grafici interattivi con Plotly

## 📚 Risorse Utili

### Dati

- [Football-Data.co.uk](https://www.football-data.co.uk/) - Dati storici gratuiti
- [API-Football](https://www.api-football.com/) - API dati live

### Machine Learning

- [Scikit-learn](https://scikit-learn.org/) - Documentazione ML
- [Pandas](https://pandas.pydata.org/) - Manipolazione dati

### Calcio Analytics

- [StatsBomb](https://statsbomb.com/) - Analytics avanzati
- [FiveThirtyEight](https://fivethirtyeight.com/soccer-predictions/) - Predizioni

## 📞 Supporto

Per problemi o domande:

1. Controlla i log di errore
2. Verifica le dipendenze Python
3. Assicurati che tutti i file siano presenti
4. Controlla la connessione internet per download dati

## 🏆 Conclusioni

Questo sistema rappresenta un approccio moderno e scientifico all'analisi calcistica, combinando:

- **Rigorosità statistica** nell'analisi dei dati
- **Tecniche ML all'avanguardia** per le predizioni
- **Interfaccia user-friendly** per utilizzo pratico
- **Codice modulare** facilmente estendibile

Perfetto per:

- **Studenti** che vogliono imparare ML applicato
- **Appassionati di calcio** interessati all'analytics
- **Data Scientists** che cercano progetti reali
- **Sviluppatori** che vogliono espandere il sistema

---

Sviluppato con ❤️ per la community del calcio e del machine learning

## Force rebuild Dom 21 Dic 2025 10:33:33 CET
