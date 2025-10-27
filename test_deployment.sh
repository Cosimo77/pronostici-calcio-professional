#!/bin/bash

# 🚀 SCRIPT DI VERIFICA POST-DEPLOYMENT
# Da eseguire dopo che Render completa il deployment

echo "🔍 VERIFICA SISTEMA DI MONITORAGGIO"
echo "===================================="

# Sostituisci con il tuo URL Render reale
APP_URL="https://tua-app.onrender.com"

echo "📋 CHECKLIST POST-DEPLOYMENT:"
echo ""

echo "1. ✅ Verifica app principale:"
echo "   $APP_URL/enterprise"
echo ""

echo "2. 🔗 Test API Health:"
echo "   $APP_URL/api/health"
echo "   Dovrebbe restituire: {'status': 'healthy'}"
echo ""

echo "3. 📊 Test API Metrics:"
echo "   $APP_URL/api/metrics_summary"
echo "   Dovrebbe mostrare performance del sistema"
echo ""

echo "4. 🎯 NUOVO: Dashboard Monitoraggio:"
echo "   $APP_URL/monitoring"
echo "   ⭐ QUESTA È LA NOVITÀ!"
echo ""

echo "🔧 Se /monitoring ancora non funziona:"
echo "- Aspetta altri 2-3 minuti"
echo "- Controlla i logs su Render"
echo "- Riavvia il servizio dal dashboard Render"
echo ""

echo "🎉 Una volta che /monitoring funziona:"
echo "- Salva nei bookmark"
echo "- Testa il pulsante 'Aggiorna Tutto'"
echo "- Prova 'Test Predizione'"
echo "- Attiva 'Auto-Refresh'"

# Test automatico (se hai curl)
if command -v curl &> /dev/null; then
    echo ""
    echo "🧪 TEST AUTOMATICO API:"
    echo "curl -s $APP_URL/api/health | head -100"
    echo "(Sostituisci URL e esegui manualmente)"
fi