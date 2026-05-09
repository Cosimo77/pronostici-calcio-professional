#!/usr/bin/env python3
"""
FIX DATABASE RENDER API - Automazione Completa
Usa Render API per configurare DATABASE_URL e migrare dati automaticamente

COSA FA:
1. Trova service ID e database ID su Render
2. Ottiene connection string del database
3. Configura DATABASE_URL come environment variable
4. Triggera deploy
5. Migra i dati

REQUISITI:
- RENDER_API_KEY environment variable
- Ottieni da: https://dashboard.render.com/u/[USERNAME]/settings
"""

import json
import os
import sys
import time

import requests

# Colori
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
END = "\033[0m"

RENDER_API_BASE = "https://api.render.com/v1"


def get_api_key():
    """Ottieni API key da env"""
    api_key = os.environ.get("RENDER_API_KEY")
    if not api_key:
        print(f"{RED}❌ RENDER_API_KEY non trovato{END}")
        print(f"\n{BOLD}Ottieni API key:{END}")
        print(f"1. Vai su: {BLUE}https://dashboard.render.com/account/settings{END}")
        print(f"2. Sezione 'API Keys'")
        print(f"3. Click 'Create API Key'")
        print(f"4. Copia il key")
        print(f'5. Export: {YELLOW}export RENDER_API_KEY="rnd_xxx"{END}')
        print(f"6. Riesegui questo script\n")
        sys.exit(1)
    return api_key


def make_request(method, endpoint, api_key, data=None):
    """Helper per API calls"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    url = f"{RENDER_API_BASE}{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    else:
        raise ValueError(f"Metodo non supportato: {method}")

    return response


def find_service(api_key, service_name="pronostici-calcio-pro"):
    """Trova service ID"""
    print(f"{BOLD}[1/6] Cerco service '{service_name}'...{END}")

    response = make_request("GET", "/services", api_key)

    if response.status_code != 200:
        print(f"{RED}❌ Errore API: {response.status_code}{END}")
        print(response.text)
        return None

    services = response.json()

    for service in services:
        if service.get("service", {}).get("name") == service_name:
            service_id = service["service"]["id"]
            print(f"{GREEN}✅ Service trovato: {service_id}{END}")
            return service_id

    print(f"{RED}❌ Service non trovato{END}")
    return None


def find_database(api_key, db_name="pronostici-calcio-db"):
    """Trova database ID e connection string"""
    print(f"{BOLD}[2/6] Cerco database '{db_name}'...{END}")

    response = make_request("GET", "/postgres", api_key)

    if response.status_code != 200:
        print(f"{RED}❌ Errore API: {response.status_code}{END}")
        return None, None

    databases = response.json()

    for db in databases:
        if db.get("postgres", {}).get("name") == db_name:
            db_id = db["postgres"]["id"]
            # Connection string format
            conn_info = db["postgres"]
            user = conn_info.get("user", "postgres")
            password = conn_info.get("password", "")
            host = conn_info.get("host", "")
            database = conn_info.get("database", "pronostici_calcio_production")

            connection_string = f"postgresql://{user}:{password}@{host}/{database}"

            print(f"{GREEN}✅ Database trovato: {db_id}{END}")
            print(f"{BLUE}ℹ️  Host: {host}{END}")
            return db_id, connection_string

    print(f"{RED}❌ Database non trovato{END}")
    return None, None


def set_env_var(api_key, service_id, key, value):
    """Imposta environment variable"""
    print(f"{BOLD}[3/6] Configuro {key}...{END}")

    # Get current env vars
    response = make_request("GET", f"/services/{service_id}/env-vars", api_key)

    if response.status_code != 200:
        print(f"{RED}❌ Errore lettura env vars{END}")
        return False

    env_vars = response.json()

    # Check if exists
    existing_var = None
    for var in env_vars:
        if var.get("envVar", {}).get("key") == key:
            existing_var = var["envVar"]["id"]
            break

    if existing_var:
        # Update existing
        response = make_request("PUT", f"/services/{service_id}/env-vars/{existing_var}", api_key, {"value": value})
    else:
        # Create new
        response = make_request("POST", f"/services/{service_id}/env-vars", api_key, {"key": key, "value": value})

    if response.status_code in [200, 201]:
        print(f"{GREEN}✅ {key} configurato{END}")
        return True
    else:
        print(f"{RED}❌ Errore configurazione{END}")
        print(response.text)
        return False


def trigger_deploy(api_key, service_id):
    """Triggera deploy manuale"""
    print(f"{BOLD}[4/6] Triggero deploy...{END}")

    response = make_request("POST", f"/services/{service_id}/deploys", api_key, {"clearCache": "clear"})

    if response.status_code in [200, 201]:
        deploy_id = response.json().get("id")
        print(f"{GREEN}✅ Deploy avviato: {deploy_id}{END}")
        print(f"{YELLOW}⏳ Attendi 8-9 minuti per completamento...{END}")
        return True
    else:
        print(f"{RED}❌ Errore deploy{END}")
        print(response.text)
        return False


def wait_for_deploy(api_key, service_id, max_wait=600):
    """Attendi completamento deploy"""
    print(f"{BOLD}[5/6] Attendo deploy...{END}")

    start_time = time.time()

    while (time.time() - start_time) < max_wait:
        response = make_request("GET", f"/services/{service_id}", api_key)

        if response.status_code == 200:
            service = response.json()
            status = service.get("service", {}).get("serviceDetails", {}).get("deploy", {}).get("status")

            if status == "live":
                print(f"{GREEN}✅ Deploy completato!{END}")
                return True
            else:
                elapsed = int(time.time() - start_time)
                print(f"{BLUE}ℹ️  Status: {status} ({elapsed}s)...{END}", end="\r")
                time.sleep(10)

    print(f"{YELLOW}⚠️  Timeout attesa deploy{END}")
    return False


def migrate_data(connection_string):
    """Migra dati usando connection string"""
    print(f"{BOLD}[6/6] Migro dati...{END}")

    try:
        from datetime import datetime

        import pandas as pd
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError:
        print(f"{YELLOW}⚠️  Installo psycopg2...{END}")
        os.system(f"{sys.executable} -m pip install psycopg2-binary pandas > /dev/null 2>&1")
        from datetime import datetime

        import pandas as pd
        import psycopg2
        from psycopg2.extras import execute_values

    # Read CSV
    df = pd.read_csv("tracking_giocate.csv")

    # Connect
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    # Create table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tracking_giocate (
            id SERIAL PRIMARY KEY,
            group_id VARCHAR(50),
            bet_number INTEGER,
            tipo_bet VARCHAR(20),
            data_giocata DATE NOT NULL,
            partita VARCHAR(100) NOT NULL,
            mercato VARCHAR(100),
            quota_sistema DECIMAL(5,2),
            quota_sisal DECIMAL(5,2),
            ev_modello VARCHAR(20),
            ev_realistico VARCHAR(20),
            stake DECIMAL(10,2) NOT NULL,
            risultato VARCHAR(20),
            profit DECIMAL(10,2),
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()

    # Insert data
    records = []
    for _, row in df.iterrows():
        records.append(
            (
                str(row.get("group_id", "")) if not pd.isna(row.get("group_id")) else None,
                int(row.get("bet_number", 1)) if not pd.isna(row.get("bet_number")) else 1,
                str(row.get("tipo_bet", "SINGLE")),
                str(row.get("Data", datetime.now().strftime("%Y-%m-%d"))),
                str(row.get("Partita", "")),
                str(row.get("Mercato", "")),
                float(row.get("Quota_Sistema", 0)) if not pd.isna(row.get("Quota_Sistema")) else None,
                float(row.get("Quota_Sisal", 0)) if not pd.isna(row.get("Quota_Sisal")) else None,
                str(row.get("EV_Modello", "")) if not pd.isna(row.get("EV_Modello")) else None,
                str(row.get("EV_Realistico", "")) if not pd.isna(row.get("EV_Realistico")) else None,
                float(row.get("Stake", 0)) if not pd.isna(row.get("Stake")) else 0,
                str(row.get("Risultato", "")) if not pd.isna(row.get("Risultato")) else None,
                float(row.get("Profit", 0)) if not pd.isna(row.get("Profit")) else None,
                str(row.get("Note", "")) if not pd.isna(row.get("Note")) else None,
            )
        )

    execute_values(
        cur,
        """INSERT INTO tracking_giocate
           (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
           VALUES %s""",
        records,
    )
    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM tracking_giocate")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"{GREEN}✨ {count} record migrati!{END}")
    return True


def main():
    """Main"""
    print(f"\n{BOLD}{'='*70}{END}")
    print(f"{BOLD}  FIX DATABASE RENDER API - Automazione Completa{END}")
    print(f"{BOLD}{'='*70}{END}\n")

    # Get API key
    api_key = get_api_key()

    # Find service
    service_id = find_service(api_key)
    if not service_id:
        sys.exit(1)

    # Find database
    db_id, connection_string = find_database(api_key)
    if not db_id or not connection_string:
        sys.exit(1)

    # Set DATABASE_URL
    if not set_env_var(api_key, service_id, "DATABASE_URL", connection_string):
        sys.exit(1)

    # Trigger deploy
    if not trigger_deploy(api_key, service_id):
        sys.exit(1)

    # Wait for deploy
    deploy_ready = wait_for_deploy(api_key, service_id)

    if not deploy_ready:
        print(f"{YELLOW}⚠️  Continuo comunque con migrazione{END}")

    # Migrate data
    try:
        migrate_data(connection_string)
    except Exception as e:
        print(f"{RED}❌ Errore migrazione: {e}{END}")
        sys.exit(1)

    # Success
    print(f"\n{BOLD}{'='*70}{END}")
    print(f"{GREEN}{BOLD}🎉🎉🎉 FIX COMPLETATO! 🎉🎉🎉{END}")
    print(f"\n{BOLD}Cosa è stato fatto:{END}")
    print(f"  ✅ Service trovato su Render")
    print(f"  ✅ Database trovato e connection string ottenuto")
    print(f"  ✅ DATABASE_URL configurato come env var")
    print(f"  ✅ Deploy triggerato")
    print(f"  ✅ Dati migrati a PostgreSQL")
    print(f"\n{BOLD}Sistema PRODUCTION READY!{END}")
    print(f"{BOLD}{'='*70}{END}\n")

    print(f"{BLUE}ℹ️  Verifica su production:{END}")
    print(f"   curl https://pronostici-calcio-professional.onrender.com/api/diario/stats")


if __name__ == "__main__":
    main()
