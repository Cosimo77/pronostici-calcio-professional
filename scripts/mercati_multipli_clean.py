import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Any, Optional
from .modelli_predittivi import PronosticiCalculator
from .feature_engineering import FeatureEngineer

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MercatiMultipli:
    """Gestore per pronostici multipli mercati di scommesse"""
    
    def __init__(self):
        """Inizializza il sistema di mercati multipli"""
        # Inizializza predittore base
        try:
            self.predittore_base = PronosticiCalculator()
            # Carica dati se disponibili
            if os.path.exists('data/dataset_features.csv'):
                self.df = pd.read_csv('data/dataset_features.csv')
            else:
                self.df = None
        except Exception as e:
            logger.warning(f"Impossibile caricare modelli: {e}")
            self.predittore_base = None
            self.df = None
            
        # Inizializza feature engineer solo se abbiamo i dati
        if self.df is not None:
            try:
                self.feature_engineer = FeatureEngineer(self.df)
            except Exception as e:
                logger.warning(f"Impossibile inizializzare FeatureEngineer: {e}")
                self.feature_engineer = None
        else:
            self.feature_engineer = None
            
        # Configurazione mercati
        self.mercati_config = {
            'over_under': {'soglia': 2.5},
            'btts': {'probabilita_minima': 0.3},
            'handicap': {'margini': [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]},
            'exact_score': {'risultati_comuni': ['0-0', '1-0', '0-1', '1-1', '2-0', '0-2', '2-1', '1-2', '2-2', '3-0', '0-3', '3-1', '1-3']}
        }
    
    def predici_tutti_mercati(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Predice tutti i mercati per una partita"""
        if not self.predittore_base:
            return {'errore': 'Modelli non disponibili'}
            
        try:
            # Predizione base 1X2
            if self.df is not None:
                pred_result, pred_prob = self.predittore_base.predici_partita(squadra_casa, squadra_trasferta, self.df)
                predizione_base = {
                    'predizione': pred_result if pred_result is not None else 'D',
                    'probabilita': pred_prob if pred_prob is not None else {'H': 0.33, 'D': 0.33, 'A': 0.34},
                    'confidenza': pred_prob.get(pred_result, 0.5) if isinstance(pred_prob, dict) and pred_result is not None else 0.5
                }
            else:
                predizione_base = {
                    'predizione': 'D',
                    'probabilita': {'H': 0.33, 'D': 0.33, 'A': 0.34},
                    'confidenza': 0.5
                }
            
            # Analisi statistiche dettagliate
            stats_casa, stats_trasferta = self._analizza_statistiche_gol(squadra_casa, squadra_trasferta)
            forma_casa, forma_trasferta = self._analizza_forma_squadre(squadra_casa, squadra_trasferta)
            
            # Tutti i mercati
            risultato = {
                '1X2': self._mercato_1x2(predizione_base),
                'over_under': self._mercato_over_under(stats_casa, stats_trasferta),
                'btts': self._mercato_btts(stats_casa, stats_trasferta),
                'double_chance': self._mercato_double_chance(predizione_base),
                'handicap': self._mercato_handicap(predizione_base, stats_casa, stats_trasferta),
                'exact_score': self._mercato_exact_score(predizione_base, stats_casa, stats_trasferta),
                'metadata': {
                    'squadra_casa': squadra_casa,
                    'squadra_trasferta': squadra_trasferta,
                    'stats_casa': stats_casa,
                    'stats_trasferta': stats_trasferta,
                    'forma_casa': forma_casa,
                    'forma_trasferta': forma_trasferta
                }
            }
            
            return risultato
            
        except Exception as e:
            logger.error(f"Errore nella predizione mercati multipli: {e}")
            return {'errore': str(e)}
    
    def _analizza_statistiche_gol(self, squadra_casa: str, squadra_trasferta: str) -> tuple:
        """Analizza le statistiche sui gol delle squadre"""
        if self.df is None:
            return self._simula_statistiche_gol(squadra_casa, squadra_trasferta)
            
        try:
            # Statistiche casa
            partite_casa = self.df[self.df['HomeTeam'] == squadra_casa]
            if len(partite_casa) == 0:
                stats_casa = self._simula_statistiche_squadra(squadra_casa)
            else:
                stats_casa = {
                    'gol_segnati_media': partite_casa['FTHG'].mean(),
                    'gol_subiti_media': partite_casa['FTAG'].mean(),
                    'clean_sheet_rate': (partite_casa['FTAG'] == 0).mean(),
                    'over_15_rate': (partite_casa['FTHG'] > 1.5).mean(),
                    'btts_rate': ((partite_casa['FTHG'] > 0) & (partite_casa['FTAG'] > 0)).mean()
                }
            
            # Statistiche trasferta
            partite_trasferta = self.df[self.df['AwayTeam'] == squadra_trasferta]
            if len(partite_trasferta) == 0:
                stats_trasferta = self._simula_statistiche_squadra(squadra_trasferta)
            else:
                stats_trasferta = {
                    'gol_segnati_media': partite_trasferta['FTAG'].mean(),
                    'gol_subiti_media': partite_trasferta['FTHG'].mean(),
                    'clean_sheet_rate': (partite_trasferta['FTHG'] == 0).mean(),
                    'over_15_rate': (partite_trasferta['FTAG'] > 1.5).mean(),
                    'btts_rate': ((partite_trasferta['FTHG'] > 0) & (partite_trasferta['FTAG'] > 0)).mean()
                }
            
            return stats_casa, stats_trasferta
            
        except Exception:
            return self._simula_statistiche_gol(squadra_casa, squadra_trasferta)
    
    def _analizza_forma_squadre(self, squadra_casa: str, squadra_trasferta: str) -> tuple:
        """Analizza la forma recente delle squadre"""
        if self.df is None:
            return self._simula_forma_squadre(squadra_casa, squadra_trasferta)
            
        try:
            # Ultime 5 partite casa (ordinamento per data)
            if 'Date' in self.df.columns:
                df_sorted = self.df.sort_values('Date', ascending=False)
            else:
                df_sorted = self.df.tail(100)  # Prendi le ultime 100 righe
                
            partite_casa_recenti = df_sorted[df_sorted['HomeTeam'] == squadra_casa].head(5)
            partite_trasferta_recenti = df_sorted[df_sorted['AwayTeam'] == squadra_trasferta].head(5)
            
            forma_casa = self._calcola_forma(partite_casa_recenti, 'casa')
            forma_trasferta = self._calcola_forma(partite_trasferta_recenti, 'trasferta')
            
            return forma_casa, forma_trasferta
            
        except Exception:
            return self._simula_forma_squadre(squadra_casa, squadra_trasferta)
    
    def _calcola_forma(self, partite: pd.DataFrame, tipo: str) -> dict:
        """Calcola la forma di una squadra"""
        if len(partite) == 0:
            return {'punti': 0, 'gol_media': 1.2, 'vittorie': 0, 'pareggi': 0, 'sconfitte': 0}
            
        punti_totali = 0
        gol_totali = 0
        vittorie = pareggi = sconfitte = 0
        
        for _, partita in partite.iterrows():
            if tipo == 'casa':
                gol_fatti = partita['FTHG']
                gol_subiti = partita['FTAG']
            else:
                gol_fatti = partita['FTAG']
                gol_subiti = partita['FTHG']
                
            gol_totali += gol_fatti
            
            if gol_fatti > gol_subiti:
                punti_totali += 3
                vittorie += 1
            elif gol_fatti == gol_subiti:
                punti_totali += 1
                pareggi += 1
            else:
                sconfitte += 1
        
        return {
            'punti': punti_totali,
            'gol_media': gol_totali / len(partite),
            'vittorie': vittorie,
            'pareggi': pareggi,
            'sconfitte': sconfitte
        }
    
    def _mercato_1x2(self, predizione_base: dict) -> dict:
        """Mercato 1X2 classico"""
        return {
            'predizione': predizione_base['predizione'],
            'probabilita': predizione_base['probabilita'],
            'confidenza': predizione_base['confidenza'],
            'valore_scommessa': 'Alta' if predizione_base['confidenza'] > 0.7 else 'Media'
        }
    
    def _mercato_over_under(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Over/Under 2.5 gol"""
        soglia = self.mercati_config['over_under']['soglia']
        
        # Calcola gol attesi
        gol_attesi = stats_casa['gol_segnati_media'] + stats_trasferta['gol_segnati_media']
        
        # Probabilità Over/Under
        if gol_attesi > soglia + 0.3:
            predizione = 'Over'
            prob_over = min(0.85, 0.5 + (gol_attesi - soglia) * 0.15)
        elif gol_attesi < soglia - 0.3:
            predizione = 'Under'
            prob_over = max(0.15, 0.5 - (soglia - gol_attesi) * 0.15)
        else:
            predizione = 'Over' if gol_attesi >= soglia else 'Under'
            prob_over = 0.5 + (gol_attesi - soglia) * 0.1
        
        prob_under = 1 - prob_over
        
        return {
            'predizione': predizione,
            'probabilita': {'Over': prob_over, 'Under': prob_under},
            'gol_attesi': round(gol_attesi, 2),
            'confidenza': abs(prob_over - 0.5) * 2,
            'valore_scommessa': 'Alta' if abs(gol_attesi - soglia) > 0.5 else 'Media'
        }
    
    def _mercato_btts(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Both Teams To Score"""
        # Probabilità che entrambe segnino
        prob_casa_segna = 1 - stats_trasferta['clean_sheet_rate']
        prob_trasferta_segna = 1 - stats_casa['clean_sheet_rate']
        
        # Combina le probabilità
        prob_btts_si = prob_casa_segna * prob_trasferta_segna
        prob_btts_no = 1 - prob_btts_si
        
        # Aggiusta per i tassi BTTS storici
        btts_medio = (stats_casa['btts_rate'] + stats_trasferta['btts_rate']) / 2
        prob_btts_si = (prob_btts_si + btts_medio) / 2
        prob_btts_no = 1 - prob_btts_si
        
        predizione = 'Si' if prob_btts_si > self.mercati_config['btts']['probabilita_minima'] else 'No'
        
        return {
            'predizione': predizione,
            'probabilita': {'Si': prob_btts_si, 'No': prob_btts_no},
            'confidenza': abs(prob_btts_si - 0.5) * 2,
            'valore_scommessa': 'Alta' if abs(prob_btts_si - 0.5) > 0.2 else 'Media'
        }
    
    def _mercato_double_chance(self, predizione_base: dict) -> dict:
        """Mercato Double Chance"""
        prob = predizione_base['probabilita']
        
        # Calcola probabilità double chance
        prob_1x = prob['H'] + prob['D']  # Casa o Pareggio
        prob_x2 = prob['D'] + prob['A']  # Pareggio o Trasferta
        prob_12 = prob['H'] + prob['A']  # Casa o Trasferta
        
        # Trova la migliore opzione
        opzioni = {'1X': prob_1x, 'X2': prob_x2, '12': prob_12}
        migliore = max(opzioni.keys(), key=lambda x: opzioni[x])
        
        return {
            'predizione': migliore,
            'probabilita': opzioni,
            'confidenza': opzioni[migliore],
            'valore_scommessa': 'Alta' if opzioni[migliore] > 0.75 else 'Media'
        }
    
    def _mercato_handicap(self, predizione_base: dict, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Asian Handicap"""
        margini = self.mercati_config['handicap']['margini']
        
        # Forza relativa delle squadre
        diff_gol = stats_casa['gol_segnati_media'] - stats_trasferta['gol_segnati_media']
        diff_subiti = stats_trasferta['gol_subiti_media'] - stats_casa['gol_subiti_media']
        forza_diff = (diff_gol + diff_subiti) / 2
        
        # Migliore handicap
        handicap_consigliato = 0
        for margine in margini:
            if abs(margine - forza_diff) < abs(handicap_consigliato - forza_diff):
                handicap_consigliato = margine
        
        # Probabilità di copertura
        prob_coperto = 0.5 + (forza_diff - handicap_consigliato) * 0.2
        prob_coperto = max(0.1, min(0.9, prob_coperto))
        
        return {
            'predizione': f"Casa {handicap_consigliato:+.1f}",
            'handicap': handicap_consigliato,
            'probabilita_copertura': prob_coperto,
            'confidenza': abs(prob_coperto - 0.5) * 2,
            'forza_differenza': round(forza_diff, 2),
            'valore_scommessa': 'Alta' if abs(forza_diff) > 0.5 else 'Media'
        }
    
    def _mercato_exact_score(self, predizione_base: dict, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Risultato Esatto"""
        risultati_comuni = self.mercati_config['exact_score']['risultati_comuni']
        
        # Gol attesi per squadra
        gol_casa_attesi = stats_casa['gol_segnati_media']
        gol_trasferta_attesi = stats_trasferta['gol_segnati_media']
        
        # Probabilità per i risultati più comuni
        probabilita_risultati = {}
        
        for risultato in risultati_comuni:
            gol_c, gol_t = map(int, risultato.split('-'))
            
            # Probabilità di Poisson semplificata
            prob_casa = self._poisson_prob(gol_c, gol_casa_attesi)
            prob_trasferta = self._poisson_prob(gol_t, gol_trasferta_attesi)
            
            probabilita_risultati[risultato] = prob_casa * prob_trasferta
        
        # Normalizza le probabilità
        totale = sum(probabilita_risultati.values())
        if totale > 0:
            probabilita_risultati = {k: v/totale * 0.6 for k, v in probabilita_risultati.items()}
        
        # Risultato più probabile
        risultato_top = max(probabilita_risultati.keys(), key=lambda x: probabilita_risultati[x])
        
        return {
            'predizione': risultato_top,
            'probabilita': probabilita_risultati,
            'confidenza': probabilita_risultati[risultato_top],
            'gol_attesi': {'casa': round(gol_casa_attesi, 1), 'trasferta': round(gol_trasferta_attesi, 1)},
            'valore_scommessa': 'Media'  # Sempre media per risultato esatto
        }
    
    def _poisson_prob(self, k: int, lam: float) -> float:
        """Calcola probabilità di Poisson approssimata"""
        if lam <= 0:
            return 0.1 if k == 0 else 0.05
        try:
            from math import exp, factorial
            return (lam ** k * exp(-lam)) / factorial(k)
        except:
            # Approssimazione semplice se non abbiamo math
            if k == 0:
                return max(0.05, 1 - lam/3)
            elif k == 1:
                return max(0.1, lam/3)
            elif k == 2:
                return max(0.05, lam/6)
            else:
                return 0.05
    
    # Metodi di simulazione per quando non abbiamo dati
    def _simula_statistiche_gol(self, squadra_casa: str, squadra_trasferta: str) -> tuple:
        """Simula statistiche quando non abbiamo dati reali"""
        stats_casa = self._simula_statistiche_squadra(squadra_casa)
        stats_trasferta = self._simula_statistiche_squadra(squadra_trasferta)
        return stats_casa, stats_trasferta
    
    def _simula_statistiche_squadra(self, squadra: str) -> dict:
        """Simula statistiche per una squadra"""
        # Usa hash del nome per consistenza
        seed = hash(squadra) % 1000
        np.random.seed(seed)
        
        return {
            'gol_segnati_media': np.random.uniform(1.0, 2.5),
            'gol_subiti_media': np.random.uniform(1.0, 2.5),
            'clean_sheet_rate': np.random.uniform(0.2, 0.5),
            'over_15_rate': np.random.uniform(0.4, 0.8),
            'btts_rate': np.random.uniform(0.3, 0.7)
        }
    
    def _simula_forma_squadre(self, squadra_casa: str, squadra_trasferta: str) -> tuple:
        """Simula forma quando non abbiamo dati reali"""
        seed_casa = hash(squadra_casa) % 1000
        seed_trasferta = hash(squadra_trasferta) % 1000
        
        np.random.seed(seed_casa)
        forma_casa = {
            'punti': np.random.randint(0, 15),
            'gol_media': np.random.uniform(0.8, 2.5),
            'vittorie': np.random.randint(0, 5),
            'pareggi': np.random.randint(0, 3),
            'sconfitte': np.random.randint(0, 3)
        }
        
        np.random.seed(seed_trasferta)
        forma_trasferta = {
            'punti': np.random.randint(0, 15),
            'gol_media': np.random.uniform(0.8, 2.5),
            'vittorie': np.random.randint(0, 5),
            'pareggi': np.random.randint(0, 3),
            'sconfitte': np.random.randint(0, 3)
        }
        
        return forma_casa, forma_trasferta