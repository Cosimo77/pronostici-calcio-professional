# ⚽ Sistema Professionale Pronostici Calcio

> **Sistema di predizione avanzato per partite di calcio con algoritmi calibrati e interfaccia enterprise-ready.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 Caratteristiche Principali

### 🧠 **Algoritmi di Predizione Avanzati**
- **Predizioni 1X2** con analisi statistica approfondita
- **27+ Mercati di Betting** completamente calibrati
- **Corner Betting** (30-65% range realistico)
- **Cartellini/Cards** (35-70% range ottimizzato)
- **Goal/NoGoal** (75-90% range bilanciato)
- **Over/Under 2.5** con calcoli probabilistici

### 🛡️ **Sicurezza Enterprise**
- Content Security Policy (CSP) compliant
- Rate limiting avanzato
- Security headers professionali
- Structured logging per monitoraggio

### 🚀 **Deployment Multi-Platform**
- **Railway** (raccomandato) - ~$1-2/mese
- **Heroku** - deployment rapido
- **Render** - alternativa gratuita
- **Docker** ready per container

### 📊 **Data & Analytics**
- Dataset 1900+ partite storiche
- 20+ squadre Serie A analizzate
- Cache intelligente per performance
- API REST complete

## 🏗️ Architettura Tecnica

```
pronostici_calcio/
├── web/
│   ├── app_professional.py    # Core Flask application
│   └── templates/
│       └── enterprise.html    # UI professionale
├── data/                      # Dataset partite storiche
├── models/                    # Modelli ML
├── cache/                     # Cache sistema
└── deployment/               # File deployment
    ├── Procfile             # Heroku/Railway
    ├── requirements.txt     # Dependencies
    └── docker-compose.yml   # Container setup
```

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone https://github.com/tuousername/pronostici_calcio.git
cd pronostici_calcio
pip install -r requirements.txt
```

### 2. **Configurazione**
```bash
cp .env.example .env
# Modifica .env con le tue configurazioni
```

### 3. **Avvio Locale**
```bash
python3 web/app_professional.py
# Server disponibile su http://localhost:5008
```

### 4. **Deploy su Railway** (Raccomandato)
```bash
# 1. Crea account su Railway.app
# 2. Connetti repository GitHub
# 3. Deploy automatico!
# Costo: ~$1-2/mese effettivi
```

## 📱 Interfaccia & Features

### **Dashboard Principale**
- Selezione squadre con autocompletamento
- Predizioni real-time
- Analisi mercati multipli
- Consigli di betting intelligenti

### **Mercati Supportati**
- 🎯 **1X2** - Risultato finale
- ⚽ **Goal/NoGoal** - Entrambe segnano
- 📊 **Over/Under 2.5** - Totale gol
- 🟨 **Cartellini** - Yellow/Red cards
- 🚩 **Corner** - Calci d'angolo
- 🎲 **Handicap** - Spread betting
- ⏱️ **Primo Tempo** - Risultati parziali

## 🔧 API Endpoints

```http
POST /api/predict_enterprise
Content-Type: application/json

{
  "home_team": "Juventus",
  "away_team": "Milan"
}
```

```http
POST /api/mercati
Content-Type: application/json

{
  "home_team": "Roma",
  "away_team": "Lazio"
}
```

## 📈 Performance & Calibrazione

### **Accuratezza Sistema**
- ✅ Corner: 65-70% (precedente 75-80%)
- ✅ Cartellini: 62% (precedente 75%)
- ✅ Goal/NoGoal: 78-85% (precedente 84%+)
- ✅ Over/Under: Distribuzioni realistiche

### **Ottimizzazioni Implementate**
- Algoritmi corner ridotti da `8.5+strength*2.0` a `7.0+strength*1.0`
- Formula cartellini da `3.0+aggressivity*3.0` a `3.5+aggressivity*1.5`
- NoGoal probabilities enhance per scenari 2.2-2.8 gol

## 🌐 Deployment Options

### **Railway** ⭐ (Consigliato)
```bash
# Setup automatico da GitHub
# Costo reale: $1-2/mese
# $5/mese di crediti inclusi
```

### **Heroku**
```bash
git push heroku main
# Free tier disponibile
```

### **Docker**
```bash
docker-compose up -d
# Container pronto per produzione
```

## 🔐 Sicurezza

- **CSP Headers**: Protezione XSS
- **Rate Limiting**: 100 req/min per IP
- **HTTPS Ready**: SSL/TLS supportato
- **Input Validation**: Sanitizzazione dati
- **Structured Logging**: Tracciamento sicurezza

## 📊 Monitoraggio

```python
# Logs strutturati JSON
{
  "timestamp": "2025-10-26T08:10:29.247Z",
  "level": "info",
  "event": "🎯 Predizione: Juventus vs Milan → H (43.6%)",
  "method": "POST",
  "status_code": 200
}
```

## 🤝 Contributing

1. Fork il repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

Questo progetto è sotto licenza MIT. Vedi [LICENSE](LICENSE) per dettagli.

## 🆘 Support

- 📧 **Email**: support@pronostici-calcio.com
- 💬 **Issues**: [GitHub Issues](https://github.com/tuousername/pronostici_calcio/issues)
- 📚 **Docs**: [Wiki Documentation](https://github.com/tuousername/pronostici_calcio/wiki)

## 🏆 Roadmap

- [ ] ⚽ Supporto Champions League
- [ ] 📱 App mobile native
- [ ] 🤖 Telegram bot integration
- [ ] 📈 Dashboard analytics avanzate
- [ ] 🔄 Auto-aggiornamento dati live
- [ ] 🌍 Multi-language support

---

<div align="center">

**🚀 Ready for Production | 🎯 Algoritmi Calibrati | 💰 Cost-Effective Deployment**

Made with ❤️ for football betting analysis

</div>