#!/bin/bash
# Script per verificare se il vecchio database Render è ancora recuperabile

echo "🔍 Verifica Vecchio Database Render PostgreSQL"
echo ""

# Chiedi DATABASE_URL vecchio
read -p "📋 Hai il vecchio DATABASE_URL di Render? (y/n): " has_url

if [ "$has_url" != "y" ]; then
    echo ""
    echo "❌ Senza DATABASE_URL non possiamo recuperare i dati"
    echo ""
    echo "📋 Dove trovarlo:"
    echo "   1. Render Dashboard → Database (se ancora visibile)"
    echo "   2. Email Render con credenziali originali"
    echo "   3. File .env backups (se esiste)"
    echo ""
    echo "⚠️  NOTA: Se database era 'suspended', probabilmente già eliminato"
    exit 1
fi

read -p "Incolla DATABASE_URL completo: " db_url

if [ -z "$db_url" ]; then
    echo "❌ DATABASE_URL vuoto"
    exit 1
fi

echo ""
echo "⏳ Test connessione..."

# Test connessione con psql (se disponibile)
if command -v psql &> /dev/null; then
    psql "$db_url" -c "SELECT COUNT(*) FROM bets;" 2>&1
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Database accessibile! Posso fare dump"
        echo ""
        read -p "Vuoi fare backup completo ora? (y/n): " do_backup
        
        if [ "$do_backup" = "y" ]; then
            backup_file="render_db_backup_$(date +%Y%m%d_%H%M%S).sql"
            echo "💾 Creando backup: $backup_file"
            pg_dump "$db_url" > "$backup_file"
            echo "✅ Backup salvato: $backup_file"
            echo ""
            echo "📋 Per importare in nuovo DB:"
            echo "   psql \$NEW_DATABASE_URL < $backup_file"
        fi
    else
        echo ""
        echo "❌ Connessione fallita - Database probabilmente eliminato"
        echo ""
        echo "💡 Suggerimento: Usa dati attuali (8 bet già migliorate)"
    fi
else
    echo ""
    echo "⚠️  psql non installato"
    echo "   Install: brew install postgresql (macOS)"
    echo ""
    echo "Test connessione Python:"
    python3 << EOF
import psycopg2
try:
    conn = psycopg2.connect("$db_url")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bets;")
    count = cur.fetchone()[0]
    print(f"\n✅ Database accessibile! Bet trovate: {count}")
    print("\n💾 Esporta con:")
    print(f"   pg_dump '$db_url' > render_backup.sql")
except Exception as e:
    print(f"\n❌ Errore: {e}")
    print("\n💡 Database probabilmente già eliminato")
EOF
fi
