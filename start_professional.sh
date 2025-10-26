#!/bin/bash

# 🚀 AVVIO RAPIDO SISTEMA PROFESSIONALE
# Script per avviare rapidamente tutto il sistema con dati aggiornati

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🏆 SISTEMA PRONOSTICI CALCIO ENTERPRISE           ║"
echo "║                                                              ║"
echo "║                    🚀 AVVIO RAPIDO                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python
log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 non trovato. Installare Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
log_success "Python $PYTHON_VERSION trovato"

# Check pip
log_info "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 non trovato"
    exit 1
fi

# Installa/aggiorna dipendenze
log_info "Installando dipendenze..."
pip3 install -r requirements.txt --quiet --upgrade

# Crea directory necessarie
log_info "Creando directory..."
mkdir -p logs
mkdir -p cache
mkdir -p models/enterprise
mkdir -p backups
mkdir -p config

# Controllo file dati
log_info "Verificando file dati..."
if [ ! -f "data/dataset_features.csv" ]; then
    log_warning "Dataset non trovato. Avviando aggiornamento dati..."
    python3 aggiorna_rapido.py
fi

# Aggiornamento rapido dati REALI (se esistono script)
if [ -f "aggiornamento_dati_reali.py" ]; then
    log_info "Aggiornamento dati REALI in corso..."
    echo "1" | python3 aggiornamento_dati_reali.py
    log_success "Dati REALI aggiornati"
fi

# Training rapido modelli (se necessario)
if [ ! -d "models/enterprise" ] || [ -z "$(ls -A models/enterprise)" ]; then
    log_info "Training modelli in corso..."
    if [ -f "allena_modelli_rapido.py" ]; then
        python3 allena_modelli_rapido.py
        log_success "Modelli addestrati"
    fi
fi

# Test rapido del sistema
log_info "Test di sistema..."
python3 -c "
import pandas as pd
import sys
try:
    df = pd.read_csv('data/dataset_features.csv')
    print(f'✅ Dataset caricato: {len(df)} record')
    
    # Check modelli
    import os
    if os.path.exists('models'):
        print('✅ Directory modelli presente')
    else:
        print('⚠️ Directory modelli mancante')
        
    print('✅ Test sistema completato')
except Exception as e:
    print(f'❌ Test fallito: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    log_error "Test di sistema fallito"
    exit 1
fi

log_success "Test di sistema completati"

# Avvio sistema professionale
log_info "Avviando sistema professionale..."
echo ""
echo "🎯 OPZIONI DI AVVIO:"
echo "1) Sistema completo con monitoring (RACCOMANDATO)"
echo "2) Solo API backend"
echo "3) Test e validazione"
echo ""

# Se è passato un parametro, usa quello
if [ "$1" = "full" ]; then
    CHOICE="1"
elif [ "$1" = "api" ]; then
    CHOICE="2" 
elif [ "$1" = "test" ]; then
    CHOICE="3"
else
    read -p "Scegli opzione (1-3): " CHOICE
fi

case $CHOICE in
    1)
        log_info "Avviando sistema completo..."
        python3 run_professional_system.py
        ;;
    2)
        log_info "Avviando solo API backend..."
        python3 app_professional.py
        ;;
    3)
        log_info "Avviando test e validazione..."
        python3 test_sistema_completo.py
        ;;
    *)
        log_error "Opzione non valida"
        exit 1
        ;;
esac