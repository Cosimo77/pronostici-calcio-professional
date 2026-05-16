#!/usr/bin/env python3
"""
🎯 GENERA PREDIZIONI GIORNALIERE AUTOMATICHE
============================================

Script per generare predizioni professionali automatiche per tutte le
prossime partite Serie A. Integra The Odds API per quote reali e
calcola value betting opportunities.

Features:
- Predizioni deterministiche basate su statistiche reali
- Confronto modello vs bookmaker (EV calculation)
- Tracking automatico in CSV per analisi performance
- Filtri FASE1 validati (EV ≥25%, quote 2.8-3.5)
- Integration The Odds API (500 req/month gratis)

Output: tracking_predictions_live.csv
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Setup logging
log_file = PROJECT_ROOT / "logs" / "predizioni_automatiche.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Import moduli interni
from integrations.odds_api import OddsAPIClient  # noqa: E402
from web.app_professional import ProfessionalCalculator  # noqa: E402


class PredictionsGenerator:
    """Generatore professionale di predizioni automatiche"""

    def __init__(self):
        self.calculator = ProfessionalCalculator()
        self.odds_client = OddsAPIClient()
        self.tracking_file = PROJECT_ROOT / "tracking_predictions_live.csv"

        # Carica dati
        logger.info("🔄 Caricamento dataset features...")
        self.calculator.carica_dati(str(PROJECT_ROOT / "data" / "dataset_features.csv"))
        logger.info(f"✅ Dataset caricato: {len(self.calculator.df_features)} partite")

    def get_upcoming_matches(self, days_ahead=7):
        """
        Recupera prossime partite Serie A da The Odds API

        Args:
            days_ahead: Giorni in avanti (default 7)

        Returns:
            list: Lista dizionari con partite
        """
        try:
            logger.info(f"🔍 Recupero partite Serie A prossimi {days_ahead} giorni...")

            # The Odds API - Serie A
            matches = self.odds_client.get_upcoming_odds(
                markets="h2h", regions="eu"  # Head to head (1X2)  # Quote europee
            )

            if not matches:
                logger.warning("⚠️ Nessuna partita trovata da API")
                return []

            # Filtra solo partite entro days_ahead
            from datetime import timezone

            cutoff_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            upcoming = []

            for match in matches:
                match_time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))

                if match_time <= cutoff_date:
                    upcoming.append(
                        {
                            "data": match_time.strftime("%Y-%m-%d"),
                            "ora": match_time.strftime("%H:%M"),
                            "casa": match["home_team"],  # Già normalizzato dall'API
                            "ospite": match["away_team"],  # Già normalizzato dall'API
                            "bookmaker_odds": {
                                "casa": match.get("odds_home"),
                                "pareggio": match.get("odds_draw"),
                                "ospite": match.get("odds_away"),
                            },
                        }
                    )

            logger.info(f"✅ Trovate {len(upcoming)} partite prossimi {days_ahead} giorni")
            return upcoming

        except Exception as e:
            logger.error(f"❌ Errore recupero partite: {e}")
            return []

    def _normalize_team_name(self, team_name):
        """Normalizza nomi squadre The Odds API → dataset interno"""
        mapping = {
            "Inter Milan": "Inter",
            "AC Milan": "Milan",
            "AS Roma": "Roma",
            "Hellas Verona": "Verona",
            "Atalanta BC": "Atalanta",
            "Bologna FC": "Bologna",
            "Cagliari Calcio": "Cagliari",
            "Empoli FC": "Empoli",
            "ACF Fiorentina": "Fiorentina",
            "Genoa CFC": "Genoa",
            "Juventus": "Juventus",
            "SS Lazio": "Lazio",
            "US Lecce": "Lecce",
            "SSC Napoli": "Napoli",
            "Parma Calcio 1913": "Parma",
            "Torino FC": "Torino",
            "Udinese Calcio": "Udinese",
            "Venezia FC": "Venezia",
            "Como 1907": "Como",
            "Monza": "Monza",
        }
        return mapping.get(team_name, team_name)

    def _extract_odds(self, bookmakers):
        """Estrae quote medie da bookmakers (focus su h2h - 1X2)"""
        if not bookmakers:
            return None

        casa_odds = []
        pareggio_odds = []
        ospite_odds = []

        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == bookmaker.get("home_team"):
                            casa_odds.append(outcome["price"])
                        elif outcome["name"] == bookmaker.get("away_team"):
                            ospite_odds.append(outcome["price"])
                        else:
                            pareggio_odds.append(outcome["price"])

        # Media quote (se disponibili)
        return {
            "casa": sum(casa_odds) / len(casa_odds) if casa_odds else None,
            "pareggio": sum(pareggio_odds) / len(pareggio_odds) if pareggio_odds else None,
            "ospite": sum(ospite_odds) / len(ospite_odds) if ospite_odds else None,
        }

    def generate_predictions(self, matches):
        """
        Genera predizioni per lista partite

        Args:
            matches: Lista partite da predire

        Returns:
            list: Predizioni con EV e value betting
        """
        predictions = []

        for match in matches:
            try:
                logger.info(f"🎯 Predizione: {match['casa']} vs {match['ospite']}")

                # Genera predizione con ProfessionalCalculator
                pronostico, probabilita, confidenza = self.calculator.predici_partita(
                    squadra_casa=match["casa"], squadra_ospite=match["ospite"]
                )

                if not pronostico:
                    logger.warning("⚠️ Errore predizione: nessun risultato")
                    continue

                # Probabilità modello (chiavi: H, D, A)
                prob_casa = probabilita.get("H", 0)
                prob_x = probabilita.get("D", 0)
                prob_ospite = probabilita.get("A", 0)

                # Quote bookmaker (se disponibili)
                odds = match.get("bookmaker_odds")

                # Calcola Expected Value per ogni mercato
                ev_casa = self._calculate_ev(prob_casa, odds["casa"]) if odds and odds["casa"] else None
                ev_x = self._calculate_ev(prob_x, odds["pareggio"]) if odds and odds["pareggio"] else None
                ev_ospite = self._calculate_ev(prob_ospite, odds["ospite"]) if odds and odds["ospite"] else None

                # Identifica migliore opportunità
                best_bet = self._identify_best_bet(
                    {"Casa": ev_casa, "Pareggio": ev_x, "Ospite": ev_ospite},
                    {
                        "Casa": odds["casa"] if odds else None,
                        "Pareggio": odds["pareggio"] if odds else None,
                        "Ospite": odds["ospite"] if odds else None,
                    },
                )

                # Crea record predizione
                prediction = {
                    "Data": match["data"],
                    "Partita": f"{match['casa']} vs {match['ospite']}",
                    "Pronostico": pronostico,
                    "Prob_Casa": round(prob_casa, 3),
                    "Prob_X": round(prob_x, 3),
                    "Prob_Ospite": round(prob_ospite, 3),
                    "Quota_Casa": round(odds["casa"], 2) if odds and odds["casa"] else None,
                    "Quota_X": round(odds["pareggio"], 2) if odds and odds["pareggio"] else None,
                    "Quota_Ospite": round(odds["ospite"], 2) if odds and odds["ospite"] else None,
                    "EV_Casa": round(ev_casa, 3) if ev_casa else None,
                    "EV_X": round(ev_x, 3) if ev_x else None,
                    "EV_Ospite": round(ev_ospite, 3) if ev_ospite else None,
                    "Best_Bet": best_bet["mercato"] if best_bet else None,
                    "Best_EV": round(best_bet["ev"], 3) if best_bet else None,
                    "Value_Betting": best_bet["is_value"] if best_bet else False,
                    "Confidenza": round(confidenza, 3),
                    "Risultato_Reale": "",  # Aggiornato dopo partita
                    "Corretto": "",  # Aggiornato dopo partita
                    "Created_At": datetime.now().isoformat(),
                }

                predictions.append(prediction)

                # Log value betting opportunities
                if best_bet and best_bet["is_value"]:
                    logger.info(f"   💰 VALUE BETTING: {best_bet['mercato']} (EV: {best_bet['ev']:.1%})")
                elif best_bet:
                    logger.info(f"   ℹ️ Nessun value (best EV: {best_bet['ev']:.1%})")
                else:
                    logger.info("   ℹ️ Quote non disponibili")

            except Exception as e:
                logger.error(f"❌ Errore predizione {match['casa']} vs {match['ospite']}: {e}")
                continue

        return predictions

    def _calculate_ev(self, probability, odds):
        """Calcola Expected Value (EV)"""
        if not probability or not odds or odds <= 1.0:
            return None

        # EV = (prob * odds) - 1
        # Positivo = value betting, negativo = bookmaker favorite
        return (probability * odds) - 1.0

    def _identify_best_bet(self, evs, odds):
        """Identifica migliore opportunità betting con filtri FASE1"""
        # Rimuovi EV None
        valid_evs = {k: v for k, v in evs.items() if v is not None}

        if not valid_evs:
            return None

        # Trova EV massimo
        best_mercato = max(valid_evs, key=valid_evs.get)
        best_ev = valid_evs[best_mercato]
        best_quota = odds.get(best_mercato)

        # Filtri FASE1 validati (ROI +7.17% su backtest)
        is_value = False
        if best_quota:
            # Solo pareggi con quote 2.8-3.5 e EV ≥25%
            if best_mercato == "Pareggio":
                if 2.8 <= best_quota <= 3.5 and best_ev >= 0.25:
                    is_value = True
            # Altri mercati: EV ≥30% (più conservativo)
            else:
                if best_ev >= 0.30:
                    is_value = True

        return {"mercato": best_mercato, "ev": best_ev, "quota": best_quota, "is_value": is_value}

    def save_to_tracking(self, predictions):
        """Salva predizioni in tracking CSV (append se esiste)"""
        if not predictions:
            logger.warning("⚠️ Nessuna predizione da salvare")
            return

        df_new = pd.DataFrame(predictions)

        # Append a file esistente (o crea nuovo)
        if self.tracking_file.exists():
            df_existing = pd.read_csv(self.tracking_file)

            # Evita duplicati (stesso match stesso giorno)
            df_existing_keys = df_existing[["Data", "Partita"]].apply(lambda x: f"{x['Data']}_{x['Partita']}", axis=1)
            df_new_keys = df_new[["Data", "Partita"]].apply(lambda x: f"{x['Data']}_{x['Partita']}", axis=1)

            duplicates = df_new_keys.isin(df_existing_keys).sum()
            if duplicates > 0:
                logger.warning(f"⚠️ Rimuovi {duplicates} duplicati")
                df_new = df_new[~df_new_keys.isin(df_existing_keys)]

            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        # Salva
        df_combined.to_csv(self.tracking_file, index=False)
        logger.info(f"✅ Salvate {len(df_new)} predizioni in {self.tracking_file}")
        logger.info(f"   Totale tracking: {len(df_combined)} predizioni")

    def update_results(self):
        """
        Aggiorna risultati reali per predizioni passate
        (Da eseguire dopo le partite per calcolare accuracy)
        """
        if not self.tracking_file.exists():
            logger.warning("⚠️ File tracking non trovato")
            return

        df = pd.read_csv(self.tracking_file)

        # Filtra solo predizioni passate senza risultato
        df["Data"] = pd.to_datetime(df["Data"])
        today = datetime.now().date()

        mask_past = (df["Data"].dt.date < today) & (df["Risultato_Reale"].isna() | (df["Risultato_Reale"] == ""))
        df_to_update = df[mask_past]

        if len(df_to_update) == 0:
            logger.info("✅ Nessun risultato da aggiornare")
            return

        logger.info(f"🔄 Aggiornamento {len(df_to_update)} risultati...")

        updated = 0
        for idx, row in df_to_update.iterrows():
            try:
                # Estrai squadre da stringa "Casa vs Ospite"
                parts = row["Partita"].split(" vs ")
                if len(parts) != 2:
                    continue

                casa, ospite = parts[0].strip(), parts[1].strip()

                # Cerca nel dataset
                match_data = self.calculator.df_features[
                    (self.calculator.df_features["HomeTeam"] == casa)
                    & (self.calculator.df_features["AwayTeam"] == ospite)
                    & (pd.to_datetime(self.calculator.df_features["Date"]).dt.date == row["Data"].date())
                ]

                if len(match_data) == 0:
                    continue

                # Estrai risultato reale
                ftr = match_data.iloc[0]["FTR"]
                result_map = {"H": "Casa", "D": "Pareggio", "A": "Ospite"}
                risultato_reale = result_map.get(ftr)

                if not risultato_reale:
                    continue

                # Aggiorna CSV
                df.at[idx, "Risultato_Reale"] = risultato_reale
                df.at[idx, "Corretto"] = 1 if row["Pronostico"] == risultato_reale else 0
                updated += 1

            except Exception as e:
                logger.error(f"❌ Errore aggiornamento riga {idx}: {e}")
                continue

        # Salva aggiornamenti
        if updated > 0:
            df.to_csv(self.tracking_file, index=False)
            logger.info(f"✅ Aggiornati {updated} risultati")

            # Statistiche accuracy
            df_completed = df[df["Risultato_Reale"].notna() & (df["Risultato_Reale"] != "")]
            if len(df_completed) > 0:
                accuracy = df_completed["Corretto"].sum() / len(df_completed)
                logger.info(
                    f"📊 Accuracy totale: {accuracy:.1%} ({df_completed['Corretto'].sum()}/{len(df_completed)})"
                )
        else:
            logger.info("ℹ️ Nessun aggiornamento trovato")


def main():
    """Entry point script"""
    print("=" * 70)
    print("🎯 GENERA PREDIZIONI GIORNALIERE AUTOMATICHE")
    print("=" * 70)
    print()

    try:
        # Inizializza generatore
        generator = PredictionsGenerator()

        # Step 1: Aggiorna risultati predizioni passate
        logger.info("📊 Step 1: Aggiornamento risultati...")
        generator.update_results()
        print()

        # Step 2: Recupera prossime partite
        logger.info("🔍 Step 2: Recupero prossime partite...")
        matches = generator.get_upcoming_matches(days_ahead=7)

        if not matches:
            logger.warning("⚠️ Nessuna partita trovata, fine script")
            return

        print()

        # Step 3: Genera predizioni
        logger.info("🎯 Step 3: Generazione predizioni...")
        predictions = generator.generate_predictions(matches)
        print()

        # Step 4: Salva tracking
        logger.info("💾 Step 4: Salvataggio tracking...")
        generator.save_to_tracking(predictions)

        print()
        print("=" * 70)
        print("✅ PREDIZIONI GENERATE CON SUCCESSO")
        print("=" * 70)
        print(f"   Partite analizzate: {len(matches)}")
        print(f"   Predizioni create: {len(predictions)}")

        # Value betting opportunities
        value_bets = [p for p in predictions if p.get("Value_Betting")]
        if value_bets:
            print(f"   💰 Value betting: {len(value_bets)} opportunità")
            for bet in value_bets[:3]:  # Top 3
                print(f"      - {bet['Partita']} | {bet['Best_Bet']} (EV: {bet['Best_EV']:.1%})")
        else:
            print("   ℹ️ Nessuna opportunità value betting trovata")

        print()

    except Exception as e:
        logger.error(f"❌ Errore fatale: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
