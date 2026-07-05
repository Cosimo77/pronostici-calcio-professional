#!/usr/bin/env python3
"""
Script per automazione completa (cron job)
Controlla e aggiorna automaticamente senza input utente
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Trova project root (parent di scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Setup logging con path relativo
log_file = PROJECT_ROOT / "logs" / "aggiornamento_auto.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(str(log_file)), logging.StreamHandler()],
)


def should_update():
    """Determina se è necessario un aggiornamento"""
    logging.info("🔍 Controllo necessità aggiornamento...")

    try:
        # SEMPRE tenta download - lascia che lo script di download decida se c'è nuova partita
        # La logica vecchia era troppo conservativa e skippava download anche con nuovi dati

        # Controlla età delle features solo per logging
        if os.path.exists("data/dataset_features.csv"):
            df = pd.read_csv("data/dataset_features.csv", parse_dates=["Date"])
            ultima_partita = df["Date"].max()
            giorni_fa = (datetime.now() - ultima_partita).days

            logging.info(
                f"📅 Ultima partita nel dataset: {ultima_partita.strftime('%d/%m/%Y')} ({giorni_fa} giorni fa)"
            )

        # SEMPRE ritorna True per forzare controllo nuovi dati
        logging.info("✅ Eseguo controllo nuovi dati da football-data.co.uk")
        return True

    except Exception as e:
        logging.error(f"❌ Errore nel controllo: {e}")
        return True


def check_new_season_available():
    """
    Controlla se è disponibile una nuova stagione
    Returns: (is_new_season, season_name)
    """
    try:
        # Leggi file CSV più recente
        import glob

        csv_files = sorted(glob.glob("data/I1_*.csv"))
        if not csv_files:
            return False, None

        latest_csv = csv_files[-1]
        season_code = latest_csv.split("_")[1].replace(".csv", "")

        # Determina stagione attesa basata su mese corrente
        now = datetime.now()
        if now.month >= 8:
            expected_season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"
        elif now.month >= 6:
            expected_season = f"{str(now.year)[2:]}{str(now.year + 1)[2:]}"
        else:
            expected_season = f"{str(now.year - 1)[2:]}{str(now.year)[2:]}"

        # Controlla se abbiamo una stagione più recente
        if season_code >= expected_season and season_code != expected_season:
            year_start = 2000 + int(season_code[:2])
            year_end = 2000 + int(season_code[2:])
            return True, f"{year_start}-{year_end}"

        return False, None

    except Exception as e:
        logging.error(f"❌ Errore check nuova stagione: {e}")
        return False, None


def should_retrain_models():
    """
    Determina se è necessario ri-addestrare i modelli
    Criteri:
    - Domenica sera (dopo giornata di campionato)
    - Nuova stagione disponibile
    - Più di 10 nuove partite dall'ultimo training
    """
    try:
        # Check 1: È domenica sera?
        oggi = datetime.now().weekday()
        ora = datetime.now().hour

        if oggi == 6 and ora >= 20:
            logging.info("📅 Domenica sera - training schedulato")
            return True, "training_settimanale"

        # Check 2: Nuova stagione disponibile?
        is_new, season_name = check_new_season_available()
        if is_new:
            logging.info(f"🆕 Nuova stagione rilevata: {season_name}")
            return True, "nuova_stagione"

        # Check 3: Molte nuove partite?
        if os.path.exists("data/dataset_features.csv"):
            df = pd.read_csv("data/dataset_features.csv")
            # Conta partite ultimo mese
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            ultimo_mese = df[df["Date"] > (datetime.now() - pd.Timedelta(days=30))]

            if len(ultimo_mese) >= 10:
                logging.info(f"📊 {len(ultimo_mese)} nuove partite - training necessario")
                return True, "molte_partite_nuove"

        return False, None

    except Exception as e:
        logging.error(f"❌ Errore check training: {e}")
        return False, None


def run_update():
    """Esegue l'aggiornamento automatico"""
    logging.info("🚀 Avvio aggiornamento automatico...")

    # Vai nella directory corretta (project root)
    os.chdir(str(PROJECT_ROOT))

    steps = [
        ("scripts/aggiorna_stagione_corrente.py", "Aggiornamento dati stagione"),
        ("scripts/aggiorna_risultati_pending.py", "Aggiornamento risultati predizioni pending"),
        ("scripts/analizza_dati.py", "Creazione dataset pulito"),
        ("scripts/feature_engineering.py", "Generazione features"),
    ]

    success_count = 0

    for script, description in steps:
        logging.info(f"🔄 {description}...")
        try:
            result = subprocess.run([sys.executable, script], capture_output=True, text=True, check=True)
            logging.info(f"✅ {description} completato")
            success_count += 1

            # Log solo le parti importanti dell'output
            if "partite" in result.stdout.lower():
                for line in result.stdout.split("\n"):
                    if "partite" in line.lower() or "ultima partita" in line.lower():
                        logging.info(f"📊 {line.strip()}")

        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore in {script}: {e}")
            if e.stdout:
                logging.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logging.error(f"STDERR: {e.stderr}")

    # Riqualifica modelli se necessario (logica migliorata)
    should_train, reason = should_retrain_models()

    if should_train:
        logging.info(f"🤖 Ri-addestramento modelli necessario: {reason}")
        try:
            result = subprocess.run(
                [sys.executable, "scripts/modelli_predittivi.py"],
                capture_output=True,
                text=True,
                check=True,
                timeout=600,  # 10 minuti timeout
            )
            logging.info("✅ Modelli riqualificati con successo")
            success_count += 1

            # Notifica importante
            logging.info("=" * 60)
            logging.info("🎉 MODELLI ML AGGIORNATI - SISTEMA PRONTO")
            logging.info("=" * 60)

        except subprocess.TimeoutExpired:
            logging.error("❌ Timeout riqualifica modelli (>10 min)")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Errore riqualifica modelli: {e}")
            if e.stderr:
                logging.error(f"STDERR: {e.stderr}")
    else:
        logging.info("ℹ️  Ri-addestramento modelli non necessario")

    return success_count


def main():
    """Processo principale automatico"""

    logging.info("=" * 60)
    logging.info("🤖 AGGIORNAMENTO AUTOMATICO AVVIATO")
    logging.info("=" * 60)

    try:
        if should_update():
            # Salva stato pre-aggiornamento
            old_season = get_current_season_info()

            success = run_update()

            # Salva stato post-aggiornamento
            new_season = get_current_season_info()

            # Check se nuova stagione rilevata
            if old_season != new_season:
                logging.info("=" * 60)
                logging.info(f"🆕 NUOVA STAGIONE DISPONIBILE: {new_season}")
                logging.info("   Modelli verranno ri-addestrati automaticamente")
                logging.info("=" * 60)

                # Salva notifica in file per consultazione futura
                save_update_notification(new_season)

            if success >= 4:  # Almeno i 4 step base
                logging.info("🎉 Aggiornamento automatico completato con successo!")
                save_last_update_status(True, success)
            else:
                logging.warning(f"⚠️  Aggiornamento parziale: {success} step completati")
                save_last_update_status(False, success)
        else:
            logging.info("✅ Nessun aggiornamento necessario")

    except Exception as e:
        logging.error(f"💥 Errore critico: {e}")
        save_last_update_status(False, 0, str(e))
        sys.exit(1)

    logging.info("🏁 Aggiornamento automatico terminato")


def get_current_season_info():
    """Ottiene info stagione corrente"""
    try:
        import glob

        csv_files = sorted(glob.glob("data/I1_*.csv"))
        if csv_files:
            latest = csv_files[-1]
            season_code = latest.split("_")[1].replace(".csv", "")
            year_start = 2000 + int(season_code[:2])
            year_end = 2000 + int(season_code[2:])
            return f"{year_start}-{year_end}"
        return "unknown"
    except Exception:
        return "unknown"


def save_update_notification(season_name):
    """Salva notifica nuova stagione in file"""
    try:
        notification_file = PROJECT_ROOT / "logs" / "season_notifications.log"
        with open(notification_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} - NUOVA STAGIONE: {season_name}\n")
    except Exception as e:
        logging.error(f"❌ Errore salvataggio notifica: {e}")


def save_last_update_status(success, steps_completed, error_msg=None):
    """Salva stato ultimo aggiornamento"""
    try:
        status_file = PROJECT_ROOT / "update_info.txt"
        with open(status_file, "w") as f:
            f.write(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Success: {success}\n")
            f.write(f"Steps Completed: {steps_completed}\n")
            if error_msg:
                f.write(f"Error: {error_msg}\n")

            # Info dataset
            if os.path.exists("data/dataset_features.csv"):
                df = pd.read_csv("data/dataset_features.csv")
                f.write(f"Total Matches: {len(df)}\n")
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                    f.write(f"Latest Match: {df['Date'].max()}\n")

            # Info stagione
            season = get_current_season_info()
            f.write(f"Current Season: {season}\n")

    except Exception as e:
        logging.error(f"❌ Errore salvataggio status: {e}")


if __name__ == "__main__":
    main()
