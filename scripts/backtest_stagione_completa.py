#!/usr/bin/env python3
"""
🔬 BACKTEST STAGIONE COMPLETA 2025-26
====================================

Script per validare sistema predittivo su partite storiche.
Simula predizioni "al momento" usando solo dati precedenti.

Features:
- Backtest walk-forward (usa solo dati passati)
- Calcolo accuracy, ROI, distribuzione predizioni
- Output CSV separato (NON modifica tracking live)
- Safe: Zero impatto su codice produzione

Output: backtest_stagione_2025_26_results.csv
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Import ProfessionalCalculator (usa codice esistente)
from web.app_professional import ProfessionalCalculator  # noqa: E402


class BacktestEngine:
    """Engine per backtest walk-forward su dati storici"""

    def __init__(self, max_matches=None):
        """
        Args:
            max_matches: Limite partite per test (None = tutte)
        """
        self.max_matches = max_matches
        self.results = []

        logger.info("🔄 Caricamento dataset completo...")
        self.df_full = pd.read_csv(PROJECT_ROOT / "data" / "dataset_features.csv")
        self.df_full["Date"] = pd.to_datetime(self.df_full["Date"])

        # Filtra stagione 2025-26
        self.df_season = self.df_full[self.df_full["Date"] >= "2025-08-01"].copy()
        self.df_season = self.df_season.sort_values("Date").reset_index(drop=True)

        if self.max_matches:
            self.df_season = self.df_season.head(self.max_matches)

        logger.info(f"✅ Dataset caricato: {len(self.df_season)} partite da testare")
        logger.info(f"📅 Periodo: {self.df_season['Date'].min().date()} → {self.df_season['Date'].max().date()}")

    def run_backtest(self):
        """Esegue backtest walk-forward su tutte le partite"""

        logger.info(f"\n🚀 INIZIO BACKTEST SU {len(self.df_season)} PARTITE\n")
        logger.info("=" * 70)

        for idx, row in self.df_season.iterrows():
            match_date = row["Date"]
            home = row["HomeTeam"]
            away = row["AwayTeam"]
            result = row["FTR"]

            # Progress log ogni 10 partite
            if (idx + 1) % 10 == 0:
                logger.info(f"Progress: {idx + 1}/{len(self.df_season)} partite")

            try:
                # Crea dataset SOLO con dati precedenti (walk-forward)
                df_before = self.df_full[self.df_full["Date"] < match_date].copy()

                # Salva temporaneamente dataset filtrato
                temp_file = PROJECT_ROOT / "temp_backtest_data.csv"
                df_before.to_csv(temp_file, index=False)

                # Inizializza calculator con dati storici
                calc = ProfessionalCalculator()
                calc.carica_dati(str(temp_file))

                # Genera predizione
                prediction, probabilita, confidenza = calc.predici_partita(home, away)

                # Cleanup temp file
                if temp_file.exists():
                    temp_file.unlink()

                if prediction:
                    # Estrai probabilità (formato: {'H': 0.5, 'D': 0.3, 'A': 0.2})
                    prob_casa = probabilita.get("H", 0)
                    prob_x = probabilita.get("D", 0)
                    prob_ospite = probabilita.get("A", 0)

                    # La predizione è già 'H', 'D', o 'A'
                    # Determina probabilità associata
                    if prediction == "H":
                        prob_pred = prob_casa
                    elif prediction == "D":
                        prob_pred = prob_x
                    else:  # 'A'
                        prob_pred = prob_ospite

                    # Verifica correttezza
                    correct = prediction == result

                    # Salva risultato
                    self.results.append(
                        {
                            "Data": match_date.date(),
                            "Partita": f"{home} vs {away}",
                            "Casa": home,
                            "Ospite": away,
                            "Risultato_Reale": result,
                            "Predizione": prediction,
                            "Corretto": correct,
                            "Prob_Casa": round(prob_casa, 3),
                            "Prob_X": round(prob_x, 3),
                            "Prob_Ospite": round(prob_ospite, 3),
                            "Prob_Predizione": round(prob_pred, 3),
                            "Confidenza": round(confidenza, 3),
                            "N_Partite_Dataset": len(df_before),
                        }
                    )

                else:
                    logger.warning(f"⚠️ Skip {home} vs {away}: dati insufficienti")

            except Exception as e:
                logger.error(f"❌ Errore {home} vs {away}: {e}")
                continue

        logger.info("=" * 70)
        logger.info(f"✅ Backtest completato: {len(self.results)} predizioni generate\n")

        return self.results

    def generate_report(self):
        """Genera report statistico dei risultati"""

        if not self.results:
            logger.error("❌ Nessun risultato disponibile")
            return

        df_results = pd.DataFrame(self.results)

        # Calcolo metriche
        total = len(df_results)
        correct = df_results["Corretto"].sum()
        accuracy = (correct / total) * 100

        # Accuracy per tipo predizione
        acc_casa = df_results[df_results["Predizione"] == "H"]["Corretto"].mean() * 100
        acc_x = df_results[df_results["Predizione"] == "D"]["Corretto"].mean() * 100
        acc_ospite = df_results[df_results["Predizione"] == "A"]["Corretto"].mean() * 100

        # Distribuzione predizioni
        dist = df_results["Predizione"].value_counts()

        # Distribuzione risultati reali
        dist_real = df_results["Risultato_Reale"].value_counts()

        print("\n" + "=" * 70)
        print("📊 REPORT BACKTEST STAGIONE 2025-26")
        print("=" * 70)
        print()
        print(f"🎯 ACCURACY GLOBALE")
        print(f"   Totale partite: {total}")
        print(f"   Corrette: {correct}")
        print(f"   Accuracy: {accuracy:.1f}%")
        print()
        print("=" * 70)
        print()
        print("📈 ACCURACY PER TIPO PREDIZIONE")
        print(f"   Casa (H):    {acc_casa:.1f}% ({dist.get('H', 0)} predizioni)")
        print(f"   Pareggio (D): {acc_x:.1f}% ({dist.get('D', 0)} predizioni)")
        print(f"   Ospite (A):  {acc_ospite:.1f}% ({dist.get('A', 0)} predizioni)")
        print()
        print("=" * 70)
        print()
        print("🎲 DISTRIBUZIONE PREDIZIONI SISTEMA")
        for pred_type, count in dist.items():
            pct = (count / total) * 100
            pred_name = {"H": "Casa", "D": "Pareggio", "A": "Ospite"}[pred_type]
            print(f"   {pred_name}: {count} ({pct:.1f}%)")
        print()
        print("=" * 70)
        print()
        print("⚽ DISTRIBUZIONE RISULTATI REALI")
        for result_type, count in dist_real.items():
            pct = (count / total) * 100
            result_name = {"H": "Casa", "D": "Pareggio", "A": "Ospite"}[result_type]
            print(f"   {result_name}: {count} ({pct:.1f}%)")
        print()
        print("=" * 70)
        print()
        print("💡 INTERPRETAZIONE")
        print()
        if accuracy > 45:
            print("   ✅ ECCELLENTE: Accuracy >45% è sopra aspettative Serie A")
        elif accuracy > 40:
            print("   ✅ BUONO: Accuracy 40-45% è performance solida")
        elif accuracy > 35:
            print("   ⚠️ ACCETTABILE: Accuracy 35-40% è nella media")
        else:
            print("   ❌ SCARSO: Accuracy <35% vicino a scelta casuale (33%)")
        print()

        # Confronto distribuzione predizioni vs realtà
        pred_casa_pct = (dist.get("H", 0) / total) * 100
        real_casa_pct = (dist_real.get("H", 0) / total) * 100
        bias_casa = pred_casa_pct - real_casa_pct

        if abs(bias_casa) > 15:
            print(f"   ⚠️ BIAS CASA RILEVATO: Prevedi Casa {pred_casa_pct:.0f}% vs realtà {real_casa_pct:.0f}%")
            print("   → Considera ridurre Bayesian smoothing o home advantage factor")

        print()
        print("=" * 70)

        return df_results

    def save_results(self, df_results):
        """Salva risultati in CSV separato"""

        output_file = PROJECT_ROOT / "backtest_stagione_2025_26_results.csv"
        df_results.to_csv(output_file, index=False)

        logger.info(f"\n💾 Risultati salvati: {output_file}")
        logger.info(f"📁 Dimensione: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """Entry point"""

    print("\n" + "=" * 70)
    print("🔬 BACKTEST ENGINE - STAGIONE 2025-26")
    print("=" * 70)
    print()
    print("⚙️ Configurazione:")
    print("   • Modalità: Walk-forward (usa solo dati passati)")
    print("   • Sistema: ProfessionalCalculator (produzione)")
    print("   • Output: backtest_stagione_2025_26_results.csv")
    print()

    # Chiedi conferma per test limitato
    import sys

    if len(sys.argv) > 1:
        try:
            max_matches = int(sys.argv[1])
            print(f"🧪 Modalità TEST: Prime {max_matches} partite")
        except:
            max_matches = None
    else:
        max_matches = None
        print("🚀 Modalità COMPLETA: Tutte le partite stagione")

    print()
    print("=" * 70)
    print()

    # Esegui backtest
    engine = BacktestEngine(max_matches=max_matches)
    results = engine.run_backtest()

    if results:
        df_results = engine.generate_report()
        engine.save_results(df_results)

        print("\n✅ BACKTEST COMPLETATO CON SUCCESSO!")
        print()
    else:
        logger.error("❌ Nessun risultato generato")


if __name__ == "__main__":
    main()
