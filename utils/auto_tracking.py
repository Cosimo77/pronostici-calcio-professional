#!/usr/bin/env python3
"""
Auto Tracking System - Professional
Salva automaticamente predizioni e aggiorna risultati in background
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

TRACKING_FILE = "tracking_predictions_live.csv"


class AutoTracker:
    """Gestisce tracking automatico predizioni e risultati"""

    def __init__(self, tracking_file: str = TRACKING_FILE):
        self.tracking_file = tracking_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea file tracking se non esiste"""
        if not os.path.exists(self.tracking_file):
            df = pd.DataFrame(
                columns=[
                    "Data",
                    "Giornata",
                    "Casa",
                    "Ospite",
                    "Mercato",
                    "Predizione",
                    "Probabilita_Sistema",
                    "Quota",
                    "EV_%",
                    "Risultato_Reale",
                    "Corretto",
                    "Profit",
                    "Note",
                ]
            )
            df.to_csv(self.tracking_file, index=False)
            logger.info(f"✅ File tracking creato: {self.tracking_file}")

    def track_prediction(
        self,
        casa: str,
        ospite: str,
        mercato: str,
        predizione: str,
        probabilita: float,
        quota: Optional[float] = None,
        ev_pct: Optional[float] = None,
        giornata: int = 0,
        note: str = "",
    ) -> bool:
        """
        Salva predizione nel tracking CSV

        Args:
            casa: Squadra casa
            ospite: Squadra ospite
            mercato: Tipo mercato (1X2, OU25, GGNG, ecc.)
            predizione: Esito predetto (Casa, Pareggio, Away, Over, Under, GG, NG)
            probabilita: Probabilità sistema (0-1)
            quota: Quota bookmaker (opzionale)
            ev_pct: Expected Value % (opzionale)
            giornata: Numero giornata
            note: Note aggiuntive

        Returns:
            True se salvato con successo
        """
        try:
            # Leggi file esistente
            if os.path.exists(self.tracking_file):
                df = pd.read_csv(self.tracking_file)
            else:
                df = pd.DataFrame()

            # Prepara nuova riga
            new_row = {
                "Data": datetime.now().strftime("%Y-%m-%d"),
                "Giornata": giornata,
                "Casa": casa,
                "Ospite": ospite,
                "Mercato": mercato,
                "Predizione": predizione,
                "Probabilita_Sistema": round(probabilita, 3),
                "Quota": round(quota, 2) if quota else "",
                "EV_%": round(ev_pct, 1) if ev_pct else "",
                "Risultato_Reale": "",  # Sarà aggiornato dopo
                "Corretto": "",
                "Profit": "",
                "Note": note,
            }

            # Aggiungi al dataframe
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Salva
            df.to_csv(self.tracking_file, index=False)

            logger.info(
                f"✅ Predizione tracciata: {casa} vs {ospite} | " f"{mercato}: {predizione} ({probabilita:.1%})"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Errore tracking predizione: {e}")
            return False

    def update_result(
        self, casa: str, ospite: str, data: str, risultato_reale: str, mercato: Optional[str] = None
    ) -> int:
        """
        Aggiorna risultato reale per una partita

        Args:
            casa: Squadra casa
            ospite: Squadra ospite
            data: Data partita (YYYY-MM-DD)
            risultato_reale: Risultato ('H', 'D', 'A', 'Over', 'Under', 'GG', 'NG')
            mercato: Filtra per mercato specifico (opzionale)

        Returns:
            Numero di righe aggiornate
        """
        try:
            df = pd.read_csv(self.tracking_file)

            # Trova righe da aggiornare
            mask = (
                (df["Casa"] == casa)
                & (df["Ospite"] == ospite)
                & (df["Data"] == data)
                & (df["Risultato_Reale"].isna() | (df["Risultato_Reale"] == ""))
            )

            if mercato:
                mask &= df["Mercato"] == mercato

            if mask.sum() == 0:
                logger.warning(f"⚠️ Nessuna predizione trovata: {casa} vs {ospite} ({data})")
                return 0

            # Aggiorna risultato
            df.loc[mask, "Risultato_Reale"] = risultato_reale

            # Calcola correttezza e profit per ogni riga aggiornata
            for idx in df[mask].index:
                predizione = str(df.loc[idx, "Predizione"])
                quota = df.loc[idx, "Quota"]

                # Correttezza
                corretto = self._check_correctness(predizione, risultato_reale, str(df.loc[idx, "Mercato"]))
                df.loc[idx, "Corretto"] = corretto

                # Profit (stake = 1 unità)
                if pd.notna(quota) and quota != "":
                    quota_val = float(str(quota))
                    if corretto:
                        profit = quota_val - 1.0  # Vince: quota - stake
                    else:
                        profit = -1.0  # Perde: -stake
                    df.loc[idx, "Profit"] = round(profit, 2)

            # Salva
            df.to_csv(self.tracking_file, index=False)

            updated = mask.sum()
            logger.info(f"✅ Aggiornate {updated} predizioni per {casa} vs {ospite}")
            return updated

        except Exception as e:
            logger.error(f"❌ Errore aggiornamento risultato: {e}")
            return 0

    def _check_correctness(self, predizione: str, risultato: str, mercato: str) -> bool:
        """Controlla se predizione è corretta"""

        # Normalizza stringhe
        pred = str(predizione).strip().lower()
        res = str(risultato).strip().lower()

        # 1X2
        if mercato == "1X2":
            mapping = {
                "casa": "h",
                "home": "h",
                "1": "h",
                "pareggio": "d",
                "draw": "d",
                "x": "d",
                "away": "a",
                "trasferta": "a",
                "2": "a",
            }
            return mapping.get(pred) == res.lower()

        # Over/Under
        if "ou25" in mercato.lower() or "over_under" in mercato.lower():
            return pred == res  # 'over' == 'over', 'under' == 'under'

        # Goal/Goal
        if "gg" in mercato.lower() or "goal_goal" in mercato.lower():
            return pred == res  # 'gg' == 'gg', 'ng' == 'ng'

        # Default: confronto diretto
        return pred == res

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Calcola statistiche predizioni

        Args:
            days: Giorni di lookback

        Returns:
            Dict con statistiche
        """
        try:
            df = pd.read_csv(self.tracking_file)

            # Filtra solo con risultato
            df_completed = df[df["Risultato_Reale"].notna() & (df["Risultato_Reale"] != "")]

            if len(df_completed) == 0:
                return {"total_predictions": 0, "accuracy": 0.0, "roi_pct": 0.0, "total_profit": 0.0}

            # Filtra ultimi N giorni
            df_completed["Data"] = pd.to_datetime(df_completed["Data"])
            cutoff = datetime.now() - pd.Timedelta(days=days)
            df_period = df_completed[df_completed["Data"] >= cutoff]

            if len(df_period) == 0:
                df_period = df_completed  # Fallback a tutti i dati

            # Calcola metriche
            total = len(df_period)
            correct = df_period["Corretto"].sum()
            accuracy = correct / total if total > 0 else 0.0

            # Profit
            df_period["Profit"] = pd.to_numeric(df_period["Profit"], errors="coerce")
            total_profit = df_period["Profit"].sum()
            roi_pct = (total_profit / total * 100) if total > 0 else 0.0

            return {
                "total_predictions": int(total),
                "correct_predictions": int(correct),
                "accuracy": round(accuracy, 4),
                "accuracy_pct": round(accuracy * 100, 2),
                "total_profit": round(total_profit, 2),
                "roi_pct": round(roi_pct, 2),
                "days_window": days,
            }

        except Exception as e:
            logger.error(f"❌ Errore calcolo stats: {e}")
            return {}


# Singleton instance
_tracker_instance = None


def get_tracker() -> AutoTracker:
    """Ottieni istanza singleton del tracker"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = AutoTracker()
    return _tracker_instance
