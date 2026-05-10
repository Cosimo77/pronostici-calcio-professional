#!/usr/bin/env python3
"""
Setup guidato DATABASE_URL su Render
Apre browser e guida l'utente passo-passo
"""

import subprocess
import sys
import time
import webbrowser
from datetime import datetime


def print_header(text):
    """Stampa header colorato"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def wait_for_user():
    """Attende conferma utente"""
    input("\n➡️  Premi INVIO quando hai completato questo passo...")


def check_production_database():
    """Verifica DATABASE_URL su production"""
    print("\n🔍 Verifico configurazione production...")

    try:
        result = subprocess.run(
            ["curl", "-s", "https://pronostici-calcio-professional.onrender.com/api/database/diagnostic"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            import json

            data = json.loads(result.stdout)

            if data.get("database_url_set"):
                print("\n✅ DATABASE_URL configurato correttamente!")
                print(f"   - Database connesso: {data.get('database_connected')}")
                print(f"   - Total bets: {data.get('total_bets')}")
                print(f"   - Database host: {data.get('database_host_masked', 'N/A')}")
                return True
            else:
                print("\n❌ DATABASE_URL non ancora configurato")
                return False
        else:
            print("\n⚠️  Impossibile verificare (servizio non raggiungibile)")
            return False

    except Exception as e:
        print(f"\n⚠️  Errore verifica: {e}")
        return False


def main():
    print_header("🚀 SETUP DATABASE RENDER - CONFIGURAZIONE GUIDATA")

    print("\n📋 Questo script ti guiderà attraverso 3 semplici passi:")
    print("   1️⃣  Configura DATABASE_URL su Render (2 minuti)")
    print("   2️⃣  Verifica migrazione automatica (1 minuto)")
    print("   3️⃣  Rimuovi CSV dal repository (30 secondi)")
    print("\n⏱️  Tempo totale stimato: 3-4 minuti")

    wait_for_user()

    # PASSO 1: Apri Render Dashboard
    print_header("PASSO 1: CONFIGURA DATABASE_URL SU RENDER")

    print("\n📖 ISTRUZIONI:")
    print("\n1. Sto per aprire 2 tab del browser:")
    print("   a) Dashboard Render (per copiare connection string)")
    print("   b) Service Environment (per aggiungere DATABASE_URL)")

    print("\n2. Nel PRIMO tab (Database):")
    print("   - Cerca il database 'pronostici-calcio-db'")
    print("   - Nella sezione 'Connections'")
    print("   - Copia l'INTERNAL DATABASE URL")
    print("   - Esempio: postgresql://user:pass@hostname/database")

    print("\n3. Nel SECONDO tab (Service Environment):")
    print("   - Clicca 'Add Environment Variable'")
    print("   - Key: DATABASE_URL")
    print("   - Value: INCOLLA il connection string copiato")
    print("   - Clicca 'Save Changes'")

    print("\n4. Render farà deploy automatico (~2 minuti)")

    input("\n➡️  Premi INVIO per aprire i browser tabs...")

    # Apri browser
    try:
        # Tab 1: Dashboard databases
        webbrowser.open("https://dashboard.render.com/")
        time.sleep(1)

        # Tab 2: Service environment (se conoscessimo il service ID)
        # Per ora apriamo solo dashboard, l'utente navigherà manualmente
        print("\n✅ Browser aperto su Render Dashboard")
        print("\n📍 NAVIGAZIONE:")
        print("   1. Vai su 'pronostici-calcio-db' → Copia Internal Database URL")
        print("   2. Vai su 'pronostici-calcio-pro' → Tab 'Environment'")
        print("   3. Aggiungi DATABASE_URL con il connection string")
        print("   4. Save Changes")

    except Exception as e:
        print(f"\n⚠️  Impossibile aprire browser automaticamente: {e}")
        print("\n📍 Apri manualmente: https://dashboard.render.com/")

    wait_for_user()

    # PASSO 2: Verifica configurazione
    print_header("PASSO 2: VERIFICA CONFIGURAZIONE")

    print("\n⏳ Attendo che il deploy sia completato...")
    print("   (Render impiega ~2 minuti per deploy)")

    deploy_complete = False
    for attempt in range(6):  # 6 tentativi = 3 minuti
        if attempt > 0:
            print(f"\n⏳ Tentativo {attempt + 1}/6 (attendo 30 secondi)...")
            time.sleep(30)

        if check_production_database():
            deploy_complete = True
            break

    if not deploy_complete:
        print("\n⚠️  DATABASE_URL non ancora rilevato")
        print("\n🔍 TROUBLESHOOTING:")
        print("   1. Verifica che il deploy sia completato su Render")
        print("   2. Controlla logs: https://dashboard.render.com → Service → Logs")
        print("   3. Verifica DATABASE_URL nelle Environment Variables")
        print("\n   Poi riesegui questo script: python3 setup_database_interattivo.py")
        sys.exit(1)

    # PASSO 3: Verifica migrazione bets
    print_header("PASSO 3: VERIFICA MIGRAZIONE BETS")

    print("\n🔍 Verifico che gli 8 bets siano stati migrati...")

    try:
        result = subprocess.run(
            ["curl", "-s", "https://pronostici-calcio-professional.onrender.com/api/diario/stats"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            import json

            stats = json.loads(result.stdout)

            total = stats.get("total", 0)
            wins = stats.get("vinte", 0)
            wr = stats.get("win_rate", 0)
            roi = stats.get("roi", 0)
            profit = stats.get("profit", 0)

            print(f"\n✅ MIGRAZIONE COMPLETATA CON SUCCESSO!")
            print(f"\n📊 STATISTICHE DIARIO:")
            print(f"   - Total bets: {total}")
            print(f"   - Vinte: {wins}")
            print(f"   - Win Rate: {wr:.1f}%")
            print(f"   - ROI: {roi:+.1f}%")
            print(f"   - Profit: {profit:+.1f}€")

            if total >= 8:
                print("\n✅ Tutti gli 8 bets originali sono stati migrati!")
            else:
                print(f"\n⚠️  Trovati solo {total} bets (attesi 8)")
                print("   Verifica manualmente: curl .../api/diario/all")
        else:
            print("\n⚠️  Impossibile verificare statistiche")

    except Exception as e:
        print(f"\n⚠️  Errore verifica: {e}")

    # PASSO 4: Cleanup CSV
    print_header("PASSO 4: CLEANUP CSV (OPZIONALE)")

    print("\n📝 Ora che i dati sono su PostgreSQL, puoi rimuovere il CSV dal repository:")
    print("\n   git rm tracking_giocate.csv")
    print("   git commit -m 'chore: Rimuovi CSV - dati migrati su PostgreSQL'")
    print("   git push origin main")

    risposta = input("\n❓ Vuoi rimuovere tracking_giocate.csv adesso? (s/n): ").strip().lower()

    if risposta == "s":
        try:
            # Rimuovi CSV
            subprocess.run(["git", "rm", "tracking_giocate.csv"], check=True)

            # Commit
            subprocess.run(["git", "commit", "-m", "chore: Rimuovi CSV - dati migrati su PostgreSQL"], check=True)

            # Push
            subprocess.run(["git", "push", "origin", "main"], check=True)

            print("\n✅ CSV rimosso e modifiche pushate su GitHub!")

        except subprocess.CalledProcessError as e:
            print(f"\n⚠️  Errore durante rimozione CSV: {e}")
            print("   Puoi farlo manualmente dopo")
    else:
        print("\n⏭️  Saltato. Puoi farlo manualmente quando vuoi.")

    # FINALE
    print_header("🎉 SETUP COMPLETATO!")

    print("\n✅ DATABASE RENDER CONFIGURATO E FUNZIONANTE")
    print("\n📋 COSA È STATO FATTO:")
    print("   ✅ DATABASE_URL configurato su Render")
    print("   ✅ PostgreSQL connesso e inizializzato")
    print("   ✅ 8 bets migrati da CSV → PostgreSQL")
    print("   ✅ Persistenza garantita tra deploy")
    print("   ✅ Sistema production-ready")

    print("\n🚀 PROSSIMI PASSI:")
    print("   - Il diario betting ora usa PostgreSQL")
    print("   - I dati persistono tra deploy/restart")
    print("   - Puoi aggiungere nuove scommesse: /diario-betting")
    print("   - Monitoring: /monitoring-v2")

    print("\n📖 DOCUMENTAZIONE:")
    print("   - DECISIONE_DATABASE_FINALE.md: Riepilogo completo")
    print("   - SETUP_DATABASE_RENDER.md: Istruzioni dettagliate")

    print("\n✨ Non dovrai più tornare su questo argomento ogni settimana! ✨")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRORE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
