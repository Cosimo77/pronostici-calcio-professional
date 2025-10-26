# 🏆 Sistema di Pronostici Calcio - Versione Completa

Sistema avanzato e completamente automatizzato per l'analisi e previsione dei risultati calcistici utilizzando machine learning, automazione intelligente e monitoraggio in tempo reale.

## � Avvio Rapido

```bash
# Setup completo del sistema
python launcher.py --setup

# Avvio sistema completo
python launcher.py

# Oppure avvia servizi singoli
python launcher.py --service web
python launcher.py --service monitoring
python launcher.py --service automation
```

Accedi all'applicazione:

- **App Principale**: <http://localhost:5000>
- **Dashboard Monitoraggio**: <http://localhost:5001>

## ✨ Caratteristiche Principali

### 🎯 Core Features

- **14 Mercati di Scommesse**: 1X2, Over/Under, Goal/NoGoal, Asian Handicap, ecc.
- **Machine Learning Avanzato**: Random Forest, Gradient Boosting, Logistic Regression
- **Interface Web Responsive**: Dashboard moderna con grafici interattivi
- **API RESTful Completa**: Endpoint per tutti i mercati e analisi

### 🤖 Automazione Intelligente

- **Aggiornamento Automatico**: Dati aggiornati quotidianamente da fonti multiple
- **Riaddestramento Modelli**: Modelli ML riaddestrati settimanalmente
- **Backup Automatici**: Backup incrementali di dati e modelli
- **Health Checks**: Monitoraggio continuo dello stato del sistema

### 📊 Monitoraggio e Analytics

- **Dashboard Real-time**: Stato sistema, accuratezza predizioni, performance
- **Log Centralizzati**: Logging strutturato di tutte le operazioni
- **Metriche Avanzate**: Tracking accuratezza, tempi di risposta, errori
- **Alerting**: Notifiche automatiche per anomalie

## 🏗️ Struttura del Progetto

```text
pronostici_calcio/
├── data/                          # Dati storici e processati
│   ├── I1_2021.csv               # Dati Serie A 2020-21
│   ├── I1_2122.csv               # Dati Serie A 2021-22
│   ├── I1_2223.csv               # Dati Serie A 2022-23
│   ├── I1_2324.csv               # Dati Serie A 2023-24
│   ├── I1_2425.csv               # Dati Serie A 2024-25
│   ├── I1_2526.csv               # Dati Serie A 2025-26
│   ├── I1_2526.csv               # Dati Serie A 2025-26
│   ├── dataset_pulito.csv        # Dataset unificato e pulito
│   └── dataset_features.csv      # Dataset con features engineered
├── models/                        # Modelli addestrati
│   ├── randomforest_model.pkl
│   ├── gradientboosting_model.pkl
│   ├── logisticregression_model.pkl
│   ├── scaler.pkl
│   └── metadata.pkl
├── scripts/                       # Script Python
│   ├── scarica_dati_storici.py   # Download dati da football-data.co.uk
│   ├── analizza_dati.py          # Analisi esplorativa
│   ├── feature_engineering.py    # Creazione features
│   ├── modelli_predittivi.py     # Training modelli ML
│   └── sistema_pronostici.py     # Interfaccia utente
├── main.py                        # Script principale
└── README.md                      # Questo file
```

## 🚀 Installazione e Setup

### 1. Prerequisiti

```bash
# Python 3.8+
python3 --version

# Installa le dipendenze
pip install pandas numpy scikit-learn matplotlib seaborn requests joblib
```

### 2. Setup Automatico

```bash
# Esegui lo script principale
python3 main.py

# Seleziona l'opzione 1 per il setup completo
```

### 3. Setup Manuale (step-by-step)

```bash
# 1. Scarica dati storici
python3 scripts/scarica_dati_storici.py

# 2. Analisi esplorativa
python3 scripts/analizza_dati.py

# 3. Feature engineering
python3 scripts/feature_engineering.py

# 4. Training modelli
python3 scripts/modelli_predittivi.py

# 5. Avvia sistema pronostici
python3 scripts/sistema_pronostici.py
```

## 🎯 Utilizzo

### Menu Principale

Il sistema offre diverse opzioni:

1. **🔮 Predici una partita** - Predizione interattiva
2. **🏟️ Mostra squadre** - Lista squadre disponibili
3. **📈 Analizza forma** - Analisi forma recente squadre
4. **❌ Esci** - Chiude il sistema

### Esempio di Predizione

```text
🔮 PREDIZIONE PARTITA

Seleziona la squadra di CASA:
1. Atalanta
2. Bologna
...
20. Juventus
...

Inserisci il numero della squadra di casa: 20

Seleziona la squadra in TRASFERTA:
1. Atalanta
...
13. Inter
...

Inserisci il numero della squadra in trasferta: 13

⚽ PARTITA: Juventus vs Inter
🤖 Calcolo predizione in corso...

🎯 PREDIZIONE: Vittoria Juventus
🎲 Confidenza: 67.5%

📊 PROBABILITÀ DETTAGLIATE:
   Casa: 67.5%
   Trasferta: 20.1%
   Pareggio: 12.4%

💡 CONSIGLI SCOMMESSE:
🟢 ALTA CONFIDENZA - Consigliato scommettere
⚽ SUGGERIMENTO: Possibile Over 2.5 gol
```

## 📊 Features Utilizzate

Il sistema utilizza oltre 30 features per ogni predizione:

### Features di Forma

- Media punti ultime 5 partite
- Gol fatti/subiti ultime 5 partite
- Performance specifica casa/trasferta

### Features Comparative

- Differenza di forma tra le squadre
- Differenza attacco vs difesa
- Performance head-to-head storica

### Features Derivate

- Rapporto casa-home vs trasferta-away
- Trend di performance recente
- Statistiche scontri diretti

## 🤖 Modelli Utilizzati

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
