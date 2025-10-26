#!/usr/bin/env python3
"""
Sistema di Mercati Multipli per Scommesse Calcistiche
Estende il sistema 1X2 con mercati avanzati
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from scripts.modelli_predittivi import PronosticiCalculator
from scripts.feature_engineering import FeatureEngineer
import logging

logger = logging.getLogger(__name__)    def _analizza_statistiche_gol(self, squadra_casa: str, squadra_trasferta: str, data_riferimento: datetime) -> dict:
        """Analizza statistiche sui gol delle squadre"""
        if self.df is None:
            return self._genera_statistiche_simulate()
        
        data_limite = data_riferimento - timedelta(days=365) pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from scripts.modelli_predittivi import PronosticiCalculator
from scripts.feature_engineering import FeatureEngineer
import logging

logger = logging.getLogger(__name__)

class MercatiMultipli:
    """Sistema per predire mercati multipli di scommesse"""
    
    def __init__(self):
        self.predittore_base = PronosticiCalculator()
        
        # Carica i modelli salvati
        try:
            if hasattr(self.predittore_base, 'carica_modelli'):
                self.predittore_base.carica_modelli()
                # PronosticiCalculator non ha df_features, carica direttamente il dataset
                try:
                    # Prova a caricare il dataset direttamente
                    try:
                        import pandas as pd
                        if os.path.exists('data/dataset_features.csv'):
                            self.df = pd.read_csv('data/dataset_features.csv')
                        else:
                            self.df = None
                    except:
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
                logger.warning(f"Errore FeatureEngineer: {e}")
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
                # Predizione simulata quando non abbiamo dati
                predizione_base = self._genera_predizione_simulata(squadra_casa, squadra_trasferta)
            
            # Se abbiamo i dati, calcola features avanzate, altrimenti usa dati base
            if self.df is not None:
                features_partita = self._calcola_features_mercati(squadra_casa, squadra_trasferta)
            else:
                # Usa features simulate quando non abbiamo dati reali
                features_partita = self._genera_features_simulate(squadra_casa, squadra_trasferta)
            
            # Predici tutti i mercati
            risultati = {
                'partita': f"{squadra_casa} vs {squadra_trasferta}",
                'timestamp': datetime.now().isoformat(),
                'mercati': {
                    '1x2': self._formato_1x2(predizione_base),
                    'over_under': self._predici_over_under(features_partita),
                    'both_teams_score': self._predici_btts(features_partita),
                    'double_chance': self._predici_double_chance(predizione_base),
                    'asian_handicap': self._predici_asian_handicap(features_partita),
                    'exact_score': self._predici_exact_score(features_partita)
                },
                'confidence_generale': predizione_base.get('confidenza', 0.5),
                'raccomandazioni': self._genera_raccomandazioni(features_partita, predizione_base)
            }
            
            return risultati
            
        except Exception as e:
            logger.error(f"Errore predizione mercati: {e}")
            return {'errore': f'Errore predizione: {str(e)}'}
    
    def _genera_predizione_simulata(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Genera una predizione 1X2 simulata quando non abbiamo modelli reali"""
        import random
        
        # Simula probabilità base per 1X2
        prob_1 = random.uniform(0.25, 0.5)
        prob_X = random.uniform(0.2, 0.35)
        prob_2 = 1.0 - prob_1 - prob_X
        
        # Normalizza per essere sicuri che sommino a 1
        totale = prob_1 + prob_X + prob_2
        prob_1 /= totale
        prob_X /= totale
        prob_2 /= totale
        
        return {
            'prob_1': prob_1,
            'prob_X': prob_X,
            'prob_2': prob_2,
            'pronostico': '1' if prob_1 > max(prob_X, prob_2) else ('X' if prob_X > prob_2 else '2'),
            'confidenza': random.uniform(0.4, 0.7),
            'simulato': True
        }
    
    def _genera_features_simulate(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Genera features simulate quando non abbiamo dati reali"""
        import random
        
        # Simula statistiche base
        features = {
            'gol': {
                'casa': {
                    'gol_fatti_media': random.uniform(1.2, 2.0),
                    'gol_subiti_media': random.uniform(0.8, 1.5),
                    'over_25_freq': random.uniform(0.4, 0.7),
                    'btts_freq': random.uniform(0.3, 0.6),
                    'clean_sheet_freq': random.uniform(0.2, 0.4)
                },
                'trasferta': {
                    'gol_fatti_media': random.uniform(1.0, 1.8),
                    'gol_subiti_media': random.uniform(1.0, 1.8),
                    'over_25_freq': random.uniform(0.3, 0.6),
                    'btts_freq': random.uniform(0.2, 0.5),
                    'clean_sheet_freq': random.uniform(0.15, 0.35)
                },
                'combinato': {}
            },
            'forma': {
                'casa': {
                    'gol_fatti_ult5': random.uniform(1.2, 2.2),
                    'gol_subiti_ult5': random.uniform(0.8, 1.6),
                    'forma_offensiva': random.uniform(1.2, 2.2),
                    'forma_difensiva': random.uniform(1.0, 2.0)
                },
                'trasferta': {
                    'gol_fatti_ult5': random.uniform(1.0, 2.0),
                    'gol_subiti_ult5': random.uniform(1.0, 1.8),
                    'forma_offensiva': random.uniform(1.0, 2.0),
                    'forma_difensiva': random.uniform(0.8, 1.8)
                }
            },
            'h2h': {
                'matches': random.randint(3, 8),
                'gol_media': random.uniform(2.2, 3.2),
                'over_25_freq': random.uniform(0.4, 0.7),
                'btts_freq': random.uniform(0.3, 0.6)
            },
            'tendenze': {
                'casa_in_casa': {
                    'gol_fatti_trend': random.uniform(1.3, 2.1),
                    'gol_subiti_trend': random.uniform(0.9, 1.5)
                },
                'trasferta_in_trasferta': {
                    'gol_fatti_trend': random.uniform(1.0, 1.9),
                    'gol_subiti_trend': random.uniform(1.1, 1.7)
                }
            }
        }
        
        # Calcola valori combinati
        features['gol']['combinato'] = {
            'gol_totali_attesi': features['gol']['casa']['gol_fatti_media'] + features['gol']['trasferta']['gol_fatti_media'],
            'over_25_prob': (features['gol']['casa']['over_25_freq'] + features['gol']['trasferta']['over_25_freq']) / 2,
            'btts_prob': (features['gol']['casa']['btts_freq'] + features['gol']['trasferta']['btts_freq']) / 2,
            'clean_sheet_prob': (features['gol']['casa']['clean_sheet_freq'] + features['gol']['trasferta']['clean_sheet_freq']) / 2
        }
        
        features['forma']['bilancio_offensivo'] = features['forma']['casa']['forma_offensiva'] - features['forma']['trasferta']['forma_difensiva']
        features['forma']['bilancio_difensivo'] = features['forma']['casa']['forma_difensiva'] - features['forma']['trasferta']['forma_offensiva']
        
        return features
    
    def _genera_statistiche_simulate(self) -> dict:
        """Genera statistiche sui gol simulate"""
        import random
        return {
            'casa': {
                'gol_fatti_media': random.uniform(1.2, 2.0),
                'gol_subiti_media': random.uniform(0.8, 1.5),
                'over_25_freq': random.uniform(0.4, 0.7),
                'btts_freq': random.uniform(0.3, 0.6),
                'clean_sheet_freq': random.uniform(0.2, 0.4)
            },
            'trasferta': {
                'gol_fatti_media': random.uniform(1.0, 1.8),
                'gol_subiti_media': random.uniform(1.0, 1.8),
                'over_25_freq': random.uniform(0.3, 0.6),
                'btts_freq': random.uniform(0.2, 0.5),
                'clean_sheet_freq': random.uniform(0.15, 0.35)
            },
            'combinato': {
                'gol_totali_attesi': random.uniform(2.5, 3.2),
                'over_25_prob': random.uniform(0.45, 0.65),
                'btts_prob': random.uniform(0.35, 0.55),
                'clean_sheet_prob': random.uniform(0.2, 0.35)
            }
        }
        
    def _genera_forma_simulate(self) -> dict:
        """Genera forma squadre simulata"""
        import random
        return {
            'casa': {
                'gol_fatti_ult5': random.uniform(1.2, 2.2),
                'gol_subiti_ult5': random.uniform(0.8, 1.6),
                'forma_offensiva': random.uniform(1.2, 2.2),
                'forma_difensiva': random.uniform(1.0, 2.0)
            },
            'trasferta': {
                'gol_fatti_ult5': random.uniform(1.0, 2.0),
                'gol_subiti_ult5': random.uniform(1.0, 1.8),
                'forma_offensiva': random.uniform(1.0, 2.0),
                'forma_difensiva': random.uniform(0.8, 1.8)
            },
            'bilancio_offensivo': random.uniform(-0.5, 0.5),
            'bilancio_difensivo': random.uniform(-0.5, 0.5)
        }
        
    def _genera_h2h_simulate(self) -> dict:
        """Genera head-to-head simulato"""
        import random
        return {
            'matches': random.randint(3, 8),
            'gol_media': random.uniform(2.2, 3.2),
            'over_25_freq': random.uniform(0.4, 0.7),
            'btts_freq': random.uniform(0.3, 0.6),
            'bilancio_casa': random.uniform(-0.2, 0.4)
        }
    
    def _calcola_features_mercati(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Calcola features specifiche per mercati avanzati"""
        if self.df is None:
            return {}
            
        features = {}
        
        # Assicurati che la colonna Date sia datetime
        if 'Date' in self.df.columns:
            if self.df['Date'].dtype == 'object':
                self.df['Date'] = pd.to_datetime(self.df['Date'])
            data_riferimento = self.df['Date'].max()
        else:
            data_riferimento = datetime.now()
        
        # Analisi gol per Over/Under e BTTS
        features['gol'] = self._analizza_statistiche_gol(squadra_casa, squadra_trasferta, data_riferimento)
        
        # Analisi forma offensiva/difensiva
        features['forma'] = self._analizza_forma_offensiva_difensiva(squadra_casa, squadra_trasferta, data_riferimento)
        
        # Head to head
        features['h2h'] = self._analizza_h2h_avanzato(squadra_casa, squadra_trasferta, data_riferimento)
        
        # Tendenze recenti
        features['tendenze'] = self._analizza_tendenze_recenti(squadra_casa, squadra_trasferta, data_riferimento)
        
        return features
    
    def _analizza_statistiche_gol(self, squadra_casa: str, squadra_trasferta: str, data_riferimento) -> dict:
        """Analizza statistiche gol per mercati correlati"""
        data_limite = data_riferimento - timedelta(days=365)
        
        # Partite casa (squadra di casa)
        partite_casa = self.df[
            (self.df['Date'] >= data_limite) & 
            (self.df['HomeTeam'] == squadra_casa)
        ].tail(10)
        
        # Partite trasferta (squadra in trasferta)
        partite_trasferta = self.df[
            (self.df['Date'] >= data_limite) & 
            (self.df['AwayTeam'] == squadra_trasferta)
        ].tail(10)
        
        stats = {
            'casa': {
                'gol_fatti_media': partite_casa['FTHG'].mean() if len(partite_casa) > 0 else 1.5,
                'gol_subiti_media': partite_casa['FTAG'].mean() if len(partite_casa) > 0 else 1.0,
                'over_25_freq': ((partite_casa['FTHG'] + partite_casa['FTAG']) > 2.5).mean() if len(partite_casa) > 0 else 0.5,
                'btts_freq': ((partite_casa['FTHG'] > 0) & (partite_casa['FTAG'] > 0)).mean() if len(partite_casa) > 0 else 0.4,
                'clean_sheet_freq': (partite_casa['FTAG'] == 0).mean() if len(partite_casa) > 0 else 0.3
            },
            'trasferta': {
                'gol_fatti_media': partite_trasferta['FTAG'].mean() if len(partite_trasferta) > 0 else 1.2,
                'gol_subiti_media': partite_trasferta['FTHG'].mean() if len(partite_trasferta) > 0 else 1.3,
                'over_25_freq': ((partite_trasferta['FTHG'] + partite_trasferta['FTAG']) > 2.5).mean() if len(partite_trasferta) > 0 else 0.45,
                'btts_freq': ((partite_trasferta['FTHG'] > 0) & (partite_trasferta['FTAG'] > 0)).mean() if len(partite_trasferta) > 0 else 0.35,
                'clean_sheet_freq': (partite_trasferta['FTHG'] == 0).mean() if len(partite_trasferta) > 0 else 0.25
            }
        }
        
        # Calcola medie combinate
        stats['combinato'] = {
            'gol_totali_attesi': stats['casa']['gol_fatti_media'] + stats['trasferta']['gol_fatti_media'],
            'over_25_prob': (stats['casa']['over_25_freq'] + stats['trasferta']['over_25_freq']) / 2,
            'btts_prob': (stats['casa']['btts_freq'] + stats['trasferta']['btts_freq']) / 2,
            'clean_sheet_prob': (stats['casa']['clean_sheet_freq'] + stats['trasferta']['clean_sheet_freq']) / 2
        }
        
        return stats
    
    def _analizza_forma_squadre(self, squadra_casa: str, squadra_trasferta: str, data_riferimento: datetime) -> dict:
        """Analizza la forma recente delle squadre"""
        if self.df is None:
            return self._genera_forma_simulate()
        
        data_limite = data_riferimento - timedelta(days=90)
        
        # Ultimi 5 match per squadra casa (tutte le partite)
        partite_casa_recenti = self.df[
            (self.df['Date'] >= data_limite) & 
            ((self.df['HomeTeam'] == squadra_casa) | (self.df['AwayTeam'] == squadra_casa))
        ].tail(5)
        
        # Ultimi 5 match per squadra trasferta
        partite_trasferta_recenti = self.df[
            (self.df['Date'] >= data_limite) & 
            ((self.df['HomeTeam'] == squadra_trasferta) | (self.df['AwayTeam'] == squadra_trasferta))
        ].tail(5)
        
        def calcola_forma_squadra(partite, nome_squadra):
            gol_fatti = []
            gol_subiti = []
            
            for _, partita in partite.iterrows():
                if partita['HomeTeam'] == nome_squadra:
                    gol_fatti.append(partita['FTHG'])
                    gol_subiti.append(partita['FTAG'])
                else:
                    gol_fatti.append(partita['FTAG'])
                    gol_subiti.append(partita['FTHG'])
            
            return {
                'gol_fatti_ult5': np.mean(gol_fatti) if gol_fatti else 1.5,
                'gol_subiti_ult5': np.mean(gol_subiti) if gol_subiti else 1.0,
                'forma_offensiva': np.mean(gol_fatti) if gol_fatti else 1.5,
                'forma_difensiva': 2.0 - np.mean(gol_subiti) if gol_subiti else 1.0  # Inverte: meno gol subiti = miglior difesa
            }
        
        forma_casa = calcola_forma_squadra(partite_casa_recenti, squadra_casa)
        forma_trasferta = calcola_forma_squadra(partite_trasferta_recenti, squadra_trasferta)
        
        return {
            'casa': forma_casa,
            'trasferta': forma_trasferta,
            'bilancio_offensivo': forma_casa['forma_offensiva'] - forma_trasferta['forma_difensiva'],
            'bilancio_difensivo': forma_casa['forma_difensiva'] - forma_trasferta['forma_offensiva']
        }
    
    def _analizza_h2h_avanzato(self, squadra_casa: str, squadra_trasferta: str, data_riferimento) -> dict:
        """Analisi head-to-head avanzata"""
        h2h_matches = self.df[
            (self.df['Date'] < data_riferimento) & 
            (((self.df['HomeTeam'] == squadra_casa) & (self.df['AwayTeam'] == squadra_trasferta)) |
             ((self.df['HomeTeam'] == squadra_trasferta) & (self.df['AwayTeam'] == squadra_casa)))
        ].tail(10)
        
        if len(h2h_matches) == 0:
            return {'matches': 0, 'gol_media': 2.5, 'over_25_freq': 0.5, 'btts_freq': 0.4}
        
        gol_totali = h2h_matches['FTHG'] + h2h_matches['FTAG']
        over_25 = (gol_totali > 2.5).mean()
        btts = ((h2h_matches['FTHG'] > 0) & (h2h_matches['FTAG'] > 0)).mean()
        
        return {
            'matches': len(h2h_matches),
            'gol_media': gol_totali.mean(),
            'over_25_freq': over_25,
            'btts_freq': btts,
            'gol_casa_media': h2h_matches['FTHG'].mean(),
            'gol_trasferta_media': h2h_matches['FTAG'].mean()
        }
    
    def _analizza_tendenze_recenti(self, squadra_casa: str, squadra_trasferta: str, data_riferimento) -> dict:
        """Analizza tendenze recenti delle squadre"""
        data_limite = data_riferimento - timedelta(days=30)
        
        # Tendenze squadra casa
        recenti_casa = self.df[
            (self.df['Date'] >= data_limite) & 
            (self.df['HomeTeam'] == squadra_casa)
        ]
        
        # Tendenze squadra trasferta  
        recenti_trasferta = self.df[
            (self.df['Date'] >= data_limite) & 
            (self.df['AwayTeam'] == squadra_trasferta)
        ]
        
        return {
            'casa_in_casa': {
                'partite': len(recenti_casa),
                'gol_fatti_trend': recenti_casa['FTHG'].mean() if len(recenti_casa) > 0 else 1.5,
                'gol_subiti_trend': recenti_casa['FTAG'].mean() if len(recenti_casa) > 0 else 1.0
            },
            'trasferta_in_trasferta': {
                'partite': len(recenti_trasferta),
                'gol_fatti_trend': recenti_trasferta['FTAG'].mean() if len(recenti_trasferta) > 0 else 1.2,
                'gol_subiti_trend': recenti_trasferta['FTHG'].mean() if len(recenti_trasferta) > 0 else 1.3
            }
        }
    
    def _predici_over_under(self, features: dict) -> dict:
        """Predice mercato Over/Under 2.5 gol"""
        gol_stats = features.get('gol', {})
        forma_stats = features.get('forma', {})
        h2h_stats = features.get('h2h', {})
        
        # Calcola probabilità Over 2.5 basata su multiple fonti
        prob_over_sources = []
        
        # Da statistiche generali
        if 'combinato' in gol_stats:
            gol_attesi = gol_stats['combinato']['gol_totali_attesi']
            prob_over_sources.append(min(0.9, max(0.1, (gol_attesi - 2.5) / 2.0 + 0.5)))
            
            # Da frequenze storiche
            over_freq = gol_stats['combinato']['over_25_prob']
            prob_over_sources.append(over_freq)
        
        # Da forma recente
        if 'casa' in forma_stats and 'trasferta' in forma_stats:
            gol_forma = forma_stats['casa']['gol_fatti_ult5'] + forma_stats['trasferta']['gol_fatti_ult5']
            prob_over_sources.append(min(0.9, max(0.1, (gol_forma - 2.5) / 2.0 + 0.5)))
        
        # Da head-to-head
        if h2h_stats.get('matches', 0) > 0:
            prob_over_sources.append(h2h_stats['over_25_freq'])
        
        # Media pesata delle probabilità
        if prob_over_sources:
            prob_over = np.mean(prob_over_sources)
        else:
            prob_over = 0.5
        
        prob_under = 1 - prob_over
        
        return {
            'predizione': 'Over 2.5' if prob_over > 0.5 else 'Under 2.5',
            'probabilita': {
                'over_2_5': round(prob_over, 3),
                'under_2_5': round(prob_under, 3)
            },
            'confidenza': round(max(prob_over, prob_under), 3),
            'gol_attesi': round(gol_stats.get('combinato', {}).get('gol_totali_attesi', 2.5), 2),
            'dettagli': {
                'fonti_analizzate': len(prob_over_sources),
                'h2h_matches': h2h_stats.get('matches', 0)
            }
        }
    
    def _predici_btts(self, features: dict) -> dict:
        """Predice Both Teams to Score"""
        gol_stats = features.get('gol', {})
        forma_stats = features.get('forma', {})
        h2h_stats = features.get('h2h', {})
        
        prob_btts_sources = []
        
        # Da statistiche generali
        if 'combinato' in gol_stats:
            btts_freq = gol_stats['combinato']['btts_prob']
            prob_btts_sources.append(btts_freq)
        
        # Da forme offensive
        if 'casa' in forma_stats and 'trasferta' in forma_stats:
            casa_prob_score = min(0.9, forma_stats['casa']['forma_offensiva'] / 2.0)
            trasferta_prob_score = min(0.9, forma_stats['trasferta']['forma_offensiva'] / 2.0)
            prob_btts_sources.append(casa_prob_score * trasferta_prob_score)
        
        # Da head-to-head
        if h2h_stats.get('matches', 0) > 0:
            prob_btts_sources.append(h2h_stats['btts_freq'])
        
        # Media pesata
        if prob_btts_sources:
            prob_btts = np.mean(prob_btts_sources)
        else:
            prob_btts = 0.4
        
        prob_no_btts = 1 - prob_btts
        
        return {
            'predizione': 'Both Teams to Score' if prob_btts > 0.5 else 'No Both Teams to Score',
            'probabilita': {
                'both_teams_score': round(prob_btts, 3),
                'no_both_teams_score': round(prob_no_btts, 3)
            },
            'confidenza': round(max(prob_btts, prob_no_btts), 3),
            'dettagli': {
                'forma_offensiva_casa': forma_stats.get('casa', {}).get('forma_offensiva', 1.5),
                'forma_offensiva_trasferta': forma_stats.get('trasferta', {}).get('forma_offensiva', 1.2)
            }
        }
    
    def _predici_double_chance(self, predizione_base: dict) -> dict:
        """Predice mercato Double Chance (1X, X2, 12)"""
        prob_base = predizione_base.get('probabilita', {})
        
        prob_h = prob_base.get('H', 0.33)
        prob_d = prob_base.get('D', 0.33) 
        prob_a = prob_base.get('A', 0.33)
        
        prob_1x = prob_h + prob_d  # Casa o Pareggio
        prob_x2 = prob_d + prob_a  # Pareggio o Trasferta
        prob_12 = prob_h + prob_a  # Casa o Trasferta (no pareggio)
        
        # Determina predizione principale
        probs = {'1X': prob_1x, 'X2': prob_x2, '12': prob_12}
        predizione_dc = max(probs.keys(), key=lambda k: probs[k])
        
        return {
            'predizione': predizione_dc,
            'probabilita': {
                '1X': round(prob_1x, 3),
                'X2': round(prob_x2, 3), 
                '12': round(prob_12, 3)
            },
            'confidenza': round(max(probs.values()), 3),
            'dettagli': {
                'probabilita_base_1x2': prob_base
            }
        }
    
    def _predici_asian_handicap(self, features: dict) -> dict:
        """Predice Asian Handicap"""
        forma_stats = features.get('forma', {})
        
        # Calcola differenza di forza tra le squadre
        if 'bilancio_offensivo' in forma_stats and 'bilancio_difensivo' in forma_stats:
            bilancio = (forma_stats['bilancio_offensivo'] + forma_stats['bilancio_difensivo']) / 2
        else:
            bilancio = 0
        
        # Determina handicap suggerito
        if bilancio > 0.8:
            handicap_suggerito = -1.0
        elif bilancio > 0.4:
            handicap_suggerito = -0.5
        elif bilancio < -0.8:
            handicap_suggerito = 1.0
        elif bilancio < -0.4:
            handicap_suggerito = 0.5
        else:
            handicap_suggerito = 0.0
        
        # Calcola probabilità per vari handicap
        handicaps = {}
        for h in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
            diff_from_suggested = abs(h - handicap_suggerito)
            prob = max(0.1, 0.8 - (diff_from_suggested * 0.3))
            handicaps[f"Casa {h:+.1f}"] = round(prob, 3)
        
        predizione_handicap = f"Casa {handicap_suggerito:+.1f}"
        
        return {
            'predizione': predizione_handicap,
            'handicap_suggerito': handicap_suggerito,
            'probabilita': handicaps,
            'confidenza': round(handicaps[predizione_handicap], 3),
            'dettagli': {
                'bilancio_squadre': round(bilancio, 3),
                'forma_casa': forma_stats.get('casa', {}),
                'forma_trasferta': forma_stats.get('trasferta', {})
            }
        }
    
    def _predici_exact_score(self, features: dict) -> dict:
        """Predice risultati esatti più probabili"""
        gol_stats = features.get('gol', {})
        
        # Stima gol attesi per squadra
        gol_casa_attesi = gol_stats.get('casa', {}).get('gol_fatti_media', 1.5)
        gol_trasferta_attesi = gol_stats.get('trasferta', {}).get('gol_fatti_media', 1.2)
        
        # Calcola probabilità per risultati comuni
        risultati_prob = {}
        
        # Definisce range realistici di gol
        for gol_casa in range(0, 4):
            for gol_trasferta in range(0, 4):
                score = f"{gol_casa}-{gol_trasferta}"
                
                # Probabilità basata su distribuzione di Poisson semplificata
                prob_casa = self._poisson_approx(gol_casa, gol_casa_attesi)
                prob_trasferta = self._poisson_approx(gol_trasferta, gol_trasferta_attesi)
                
                prob_combinata = prob_casa * prob_trasferta
                risultati_prob[score] = round(prob_combinata, 4)
        
        # Ordina per probabilità
        risultati_ordinati = sorted(risultati_prob.items(), key=lambda x: x[1], reverse=True)
        
        # Top 5 risultati più probabili
        top_5 = dict(risultati_ordinati[:5])
        predizione_principale = risultati_ordinati[0][0]
        
        return {
            'predizione': predizione_principale,
            'probabilita': top_5,
            'confidenza': round(risultati_ordinati[0][1], 4),
            'gol_attesi': {
                'casa': round(gol_casa_attesi, 2),
                'trasferta': round(gol_trasferta_attesi, 2)
            },
            'dettagli': {
                'tutti_risultati_analizzati': len(risultati_prob),
                'probabilita_top_5': round(sum(top_5.values()), 4)
            }
        }
    
    def _poisson_approx(self, k: int, lam: float) -> float:
        """Approssimazione semplificata della distribuzione di Poisson"""
        if lam <= 0:
            return 0.0 if k > 0 else 1.0
        
        # Approssimazione per evitare calcoli complessi
        if k == 0:
            return np.exp(-lam)
        elif k == 1:
            return lam * np.exp(-lam)
        elif k == 2:
            return (lam**2 / 2) * np.exp(-lam)
        elif k == 3:
            return (lam**3 / 6) * np.exp(-lam)
        else:
            import math
            return (lam**k / math.factorial(k)) * np.exp(-lam)
    
    def _formato_1x2(self, predizione_base: dict) -> dict:
        """Formatta predizione 1X2 per consistency"""
        return {
            'predizione': predizione_base.get('predizione', 'D'),
            'probabilita': {
                'vittoria_casa': predizione_base.get('probabilita', {}).get('H', 0.33),
                'pareggio': predizione_base.get('probabilita', {}).get('D', 0.33),
                'vittoria_trasferta': predizione_base.get('probabilita', {}).get('A', 0.33)
            },
            'confidenza': predizione_base.get('confidenza', 0.5)
        }
    
    def _genera_raccomandazioni(self, features: dict, predizione_base: dict) -> list:
        """Genera raccomandazioni basate su tutti i mercati"""
        raccomandazioni = []
        
        # Analizza confidence generale
        confidence = predizione_base.get('confidenza', 0.5)
        
        if confidence >= 0.7:
            raccomandazioni.append({
                'tipo': 'alta_confidence',
                'messaggio': '🟢 Alta confidenza - Mercato 1X2 raccomandato',
                'priority': 1
            })
        
        # Analizza Over/Under
        gol_stats = features.get('gol', {})
        if 'combinato' in gol_stats:
            gol_attesi = gol_stats['combinato']['gol_totali_attesi']
            if gol_attesi > 3.0:
                raccomandazioni.append({
                    'tipo': 'over_gol',
                    'messaggio': f'⚽ Over 2.5 probabile ({gol_attesi:.1f} gol attesi)',
                    'priority': 2
                })
            elif gol_attesi < 2.0:
                raccomandazioni.append({
                    'tipo': 'under_gol', 
                    'messaggio': f'🛡️ Under 2.5 probabile ({gol_attesi:.1f} gol attesi)',
                    'priority': 2
                })
        
        # Analizza BTTS
        if 'combinato' in gol_stats:
            btts_prob = gol_stats['combinato']['btts_prob']
            if btts_prob > 0.6:
                raccomandazioni.append({
                    'tipo': 'btts_si',
                    'messaggio': f'🎯 Both Teams to Score probabile ({btts_prob*100:.0f}%)',
                    'priority': 3
                })
            elif btts_prob < 0.3:
                raccomandazioni.append({
                    'tipo': 'btts_no',
                    'messaggio': f'🚫 No Both Teams to Score probabile ({(1-btts_prob)*100:.0f}%)',
                    'priority': 3
                })
        
        # Ordina per priorità
        raccomandazioni.sort(key=lambda x: x['priority'])
        
        return raccomandazioni

def main():
    """Test del sistema mercati multipli"""
    print("🎲 Sistema Mercati Multipli - Test")
    print("=" * 50)
    
    mercati = MercatiMultipli()
    
    # Test con partita esempio
    squadra_casa = "Atalanta"
    squadra_trasferta = "Bologna"
    
    print(f"\n🏟️ Test: {squadra_casa} vs {squadra_trasferta}")
    
    risultati = mercati.predici_tutti_mercati(squadra_casa, squadra_trasferta)
    
    if 'errore' in risultati:
        print(f"❌ Errore: {risultati['errore']}")
        return
    
    print(f"\n📊 RISULTATI MERCATI MULTIPLI")
    print(f"Partita: {risultati['partita']}")
    print(f"Confidence generale: {risultati['confidence_generale']*100:.1f}%")
    
    # Mostra risultati per mercato
    mercati_data = risultati['mercati']
    
    print(f"\n🎯 1X2 CLASSICO:")
    m1x2 = mercati_data['1x2']
    print(f"   Predizione: {m1x2['predizione']}")
    print(f"   Casa: {m1x2['probabilita']['vittoria_casa']*100:.1f}%")
    print(f"   Pareggio: {m1x2['probabilita']['pareggio']*100:.1f}%")
    print(f"   Trasferta: {m1x2['probabilita']['vittoria_trasferta']*100:.1f}%")
    
    print(f"\n⚽ OVER/UNDER 2.5:")
    mou = mercati_data['over_under']
    print(f"   Predizione: {mou['predizione']}")
    print(f"   Over 2.5: {mou['probabilita']['over_2_5']*100:.1f}%")
    print(f"   Under 2.5: {mou['probabilita']['under_2_5']*100:.1f}%")
    print(f"   Gol attesi: {mou['gol_attesi']}")
    
    print(f"\n🎯 BOTH TEAMS TO SCORE:")
    mbtts = mercati_data['both_teams_score'] 
    print(f"   Predizione: {mbtts['predizione']}")
    print(f"   BTTS: {mbtts['probabilita']['both_teams_score']*100:.1f}%")
    print(f"   No BTTS: {mbtts['probabilita']['no_both_teams_score']*100:.1f}%")
    
    print(f"\n🔄 DOUBLE CHANCE:")
    mdc = mercati_data['double_chance']
    print(f"   Predizione: {mdc['predizione']}")
    for k, v in mdc['probabilita'].items():
        print(f"   {k}: {v*100:.1f}%")
    
    print(f"\n📏 ASIAN HANDICAP:")
    mah = mercati_data['asian_handicap']
    print(f"   Handicap suggerito: {mah['predizione']}")
    print(f"   Confidenza: {mah['confidenza']*100:.1f}%")
    
    print(f"\n🎲 EXACT SCORE (Top 3):")
    mes = mercati_data['exact_score']
    top_3 = list(mes['probabilita'].items())[:3]
    for score, prob in top_3:
        print(f"   {score}: {prob*100:.1f}%")
    
    print(f"\n💡 RACCOMANDAZIONI:")
    for racc in risultati['raccomandazioni']:
        print(f"   {racc['messaggio']}")
    
    print(f"\n✅ Test completato!")

if __name__ == "__main__":
    main()