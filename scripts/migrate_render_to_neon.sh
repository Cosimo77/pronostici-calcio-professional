#!/bin/bash
# Script Migrazione: Render PostgreSQL → Neon PostgreSQL
# Data: 4 giugno 2026

set -e  # Exit on error

echo "🔄 MIGRAZIONE RENDER → NEON POSTGRESQL"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verifica prerequisiti
echo "📋 Step 1: Verifica prerequisiti..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ psql non trovato${NC}"
    echo "Installa con: brew install postgresql"
    exit 1
fi

if ! command -v pg_dump &> /dev/null; then
    echo -e "${RED}❌ pg_dump non trovato${NC}"
    echo "Installa con: brew install postgresql"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisiti OK${NC}"
echo ""

# Step 2: Richiedi DATABASE_URL Render
echo "📥 Step 2: Backup dati da Render..."
echo ""
echo -e "${YELLOW}Vai su: https://dashboard.render.com/${NC}"
echo -e "${YELLOW}→ pronostici-calcio-db → Info → Internal Database URL${NC}"
echo ""
read -p "Incolla DATABASE_URL Render: " RENDER_DB_URL

if [ -z "$RENDER_DB_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL vuoto!${NC}"
    exit 1
fi

# Step 3: Esporta dati
BACKUP_FILE="backup_render_$(date +%Y%m%d_%H%M%S).sql"
echo ""
echo "💾 Esportazione in corso..."
echo "File: $BACKUP_FILE"
echo ""

if pg_dump "$RENDER_DB_URL" > "$BACKUP_FILE" 2>&1; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup completato: $BACKUP_SIZE${NC}"
    echo ""

    # Mostra anteprima contenuto
    echo "📊 Anteprima backup:"
    echo "---"
    grep -E "CREATE TABLE|INSERT INTO" "$BACKUP_FILE" | head -10 || echo "(nessuna tabella trovata - database vuoto?)"
    echo "---"
    echo ""
else
    echo -e "${RED}❌ Errore durante backup!${NC}"
    echo "Verifica che DATABASE_URL sia corretto"
    exit 1
fi

# Step 4: Setup Neon
echo "🆕 Step 3: Setup Neon PostgreSQL..."
echo ""
echo -e "${YELLOW}1. Vai su: https://neon.tech${NC}"
echo -e "${YELLOW}2. Registrati (FREE, no carta di credito)${NC}"
echo -e "${YELLOW}3. Create Project:${NC}"
echo "   - Nome: pronostici-calcio-production"
echo "   - Region: Europe (Frankfurt)"
echo "   - PostgreSQL: 16"
echo -e "${YELLOW}4. Copia Connection String dalla dashboard${NC}"
echo ""
read -p "Incolla DATABASE_URL Neon: " NEON_DB_URL

if [ -z "$NEON_DB_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL Neon vuoto!${NC}"
    exit 1
fi

# Step 5: Restore su Neon
echo ""
echo "📤 Step 4: Restore su Neon..."
echo ""

if psql "$NEON_DB_URL" < "$BACKUP_FILE" 2>&1; then
    echo -e "${GREEN}✅ Restore completato${NC}"
    echo ""
else
    echo -e "${RED}❌ Errore durante restore!${NC}"
    echo "Il backup è salvato in: $BACKUP_FILE"
    echo "Puoi riprovare manualmente con:"
    echo "  psql \"\$NEON_DB_URL\" < $BACKUP_FILE"
    exit 1
fi

# Step 6: Verifica migrazione
echo "🔍 Step 5: Verifica dati migrati..."
echo ""

BET_COUNT=$(psql "$NEON_DB_URL" -t -c "SELECT COUNT(*) FROM bets;" 2>/dev/null | xargs || echo "0")
GROUP_COUNT=$(psql "$NEON_DB_URL" -t -c "SELECT COUNT(*) FROM bet_groups;" 2>/dev/null | xargs || echo "0")

echo "📊 Statistiche migrazione:"
echo "   - Scommesse singole: $BET_COUNT"
echo "   - Scommesse multiple: $GROUP_COUNT"
echo ""

if [ "$BET_COUNT" -gt 0 ] || [ "$GROUP_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Dati migrati correttamente!${NC}"
else
    echo -e "${YELLOW}⚠️  Nessun dato trovato (database Render era vuoto?)${NC}"
fi
echo ""

# Step 7: Istruzioni finali
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 MIGRAZIONE COMPLETATA!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 PROSSIMI PASSI:"
echo ""
echo "1️⃣  Aggiorna Render Environment Variable:"
echo "   Dashboard: https://dashboard.render.com/"
echo "   → pronostici-calcio-pro → Environment → DATABASE_URL"
echo "   → Change from 'From Database' to 'Secret'"
echo "   → Paste:"
echo ""
echo -e "${YELLOW}$NEON_DB_URL${NC}"
echo ""
echo "2️⃣  Render farà automaticamente redeploy (2-3 minuti)"
echo ""
echo "3️⃣  Verifica app funzionante:"
echo "   curl https://pronostici-calcio-pro.onrender.com/api/health"
echo ""
echo "4️⃣  DOPO 7 giorni di test: elimina database Render"
echo "   (Dashboard → pronostici-calcio-db → Delete)"
echo ""
echo "💾 BACKUP SALVATO: $BACKUP_FILE"
echo "   (conservalo per 30 giorni come sicurezza)"
echo ""
echo -e "${GREEN}✅ Sistema ora usa Neon PostgreSQL (FREE permanente)${NC}"
