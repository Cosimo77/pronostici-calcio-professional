import pandas as pd
import numpy as np
import logging
import os
import sys
from typing import Dict, Any, Optional

# Aggiungi il percorso degli script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modelli_predittivi import PronosticiCalculator
from feature_engineering import FeatureEngineer

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
            # Carica modelli se disponibili
            if os.path.exists('models/metadata.pkl'):
                self.predittore_base.carica_modelli()
                
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
                # Carica dataset completo per feature engineering
                if os.path.exists('data/dataset_pulito.csv'):
                    df_completo = pd.read_csv('data/dataset_pulito.csv')
                    df_completo['Date'] = pd.to_datetime(df_completo['Date'])
                    self.feature_engineer = FeatureEngineer(df_completo)
                else:
                    self.feature_engineer = FeatureEngineer(self.df)
            except Exception as e:
                logger.warning(f"Impossibile inizializzare FeatureEngineer: {e}")
                self.feature_engineer = None
        else:
            self.feature_engineer = None
            
        # Configurazione mercati
        self.mercati_config = {
            'over_under': {'soglia': 2.5},
            'over_under_15': {'soglia': 1.5},
            'over_under_35': {'soglia': 3.5},
            'btts': {'probabilita_minima': 0.3},
            'handicap': {'margini': [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]},
            'exact_score': {'risultati_comuni': ['0-0', '1-0', '0-1', '1-1', '2-0', '0-2', '2-1', '1-2', '2-2', '3-0', '0-3', '3-1', '1-3']},
            'primo_tempo': {'soglia_gol': 1.5},
            'clean_sheet': {'probabilita_minima': 0.2}
        }
    
    def predici_tutti_mercati(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Predice tutti i mercati per una partita"""
        if not self.predittore_base:
            return {'errore': 'Modelli non disponibili'}
            
        try:
            # Predizione base 1X2 con fallback intelligente
            predizione_base = self._genera_predizione_base(squadra_casa, squadra_trasferta)
            
            # Analisi statistiche dettagliate
            stats_casa, stats_trasferta = self._analizza_statistiche_gol(squadra_casa, squadra_trasferta)
            forma_casa, forma_trasferta = self._analizza_forma_squadre(squadra_casa, squadra_trasferta)
            
            # Tutti i mercati
            risultato = {
                '1X2': self._mercato_1x2(predizione_base),
                'over_under': self._mercato_over_under(stats_casa, stats_trasferta),
                'over_under_15': self._mercato_over_under_15(stats_casa, stats_trasferta),
                'over_under_35': self._mercato_over_under_35(stats_casa, stats_trasferta),
                'btts': self._mercato_btts(stats_casa, stats_trasferta),
                'double_chance': self._mercato_double_chance(predizione_base),
                'handicap': self._mercato_handicap(predizione_base, stats_casa, stats_trasferta),
                'exact_score': self._mercato_exact_score(predizione_base, stats_casa, stats_trasferta),
                'prima_squadra_gol': self._mercato_prima_squadra_gol(stats_casa, stats_trasferta),
                'clean_sheet': self._mercato_clean_sheet(stats_casa, stats_trasferta),
                'primo_tempo_1x2': self._mercato_primo_tempo_1x2(predizione_base, stats_casa, stats_trasferta),
                'primo_tempo_over_under': self._mercato_primo_tempo_over_under(stats_casa, stats_trasferta),
                'cartellini_totali': self._mercato_cartellini_totali(squadra_casa, squadra_trasferta),
                'cartellini_over_under': self._mercato_cartellini_over_under(squadra_casa, squadra_trasferta),
                'calci_angolo_totali': self._mercato_calci_angolo_totali(squadra_casa, squadra_trasferta),
                'calci_angolo_over_under': self._mercato_calci_angolo_over_under(squadra_casa, squadra_trasferta),
                'metadata': {
                    'squadra_casa': squadra_casa,
                    'squadra_trasferta': squadra_trasferta,
                    'stats_casa': stats_casa,
                    'stats_trasferta': stats_trasferta,
                    'forma_casa': forma_casa,
                    'forma_trasferta': forma_trasferta
                }
            }
            
            # Genera raccomandazioni intelligenti
            risultato['raccomandazioni'] = self._genera_raccomandazioni(risultato)
            
            return risultato
            
        except Exception as e:
            logger.error(f"Errore nella predizione mercati multipli: {e}")
            return {'errore': str(e)}
    
    def _genera_predizione_base(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Genera predizione base con fallback intelligente"""
        try:
            # Prima prova con il modello ML
            if self.df is not None and self.predittore_base:
                pred_result, pred_prob = self.predittore_base.predici_partita(squadra_casa, squadra_trasferta, self.df)
                
                # Verifica che i risultati siano validi (non None e non tutti zero)
                if (pred_result is not None and pred_prob is not None and 
                    isinstance(pred_prob, dict) and 
                    sum(pred_prob.values()) > 0):
                    
                    return {
                        'predizione': pred_result,
                        'probabilita': pred_prob,
                        'confidenza': pred_prob.get(pred_result, 0.5)
                    }
                else:
                    print(f"⚠️ Modello ML ha restituito risultati non validi, uso fallback statistico")
            
            # Fallback: analisi basata su statistiche storiche
            # Usa i metodi esistenti per ottenere i dati
            stats_casa, stats_trasferta = self._analizza_statistiche_gol(squadra_casa, squadra_trasferta)
            forma_casa, forma_trasferta = self._analizza_forma_squadre(squadra_casa, squadra_trasferta)
            
            return self._predizione_statistica(squadra_casa, squadra_trasferta)
            
        except Exception as e:
            logger.warning(f"Errore predizione base: {e}, uso fallback statistico")
            # Fallback con valori di default
            return {
                'predizione': 'H',  # Casa favorita di default
                'probabilita': {'H': 0.50, 'D': 0.30, 'A': 0.20},
                'confidenza': 0.50
            }
    
    def _genera_raccomandazioni(self, risultato):
        """
        Genera raccomandazioni intelligenti basate sui risultati dei mercati
        """
        raccomandazioni = []
        
        try:
            # Analizza i mercati per le opportunità migliori
            mercati_keys = [k for k in risultato.keys() if k not in ['metadata', 'raccomandazioni', 'errore']]
            
            for nome_mercato in mercati_keys:
                dati = risultato.get(nome_mercato, {})
                if not isinstance(dati, dict) or 'predizione' not in dati:
                    continue
                    
                confidenza = dati.get('confidenza', 0)
                if confidenza <= 1:  # Se è in decimale, converte in percentuale
                    confidenza = confidenza * 100
                    
                predizione = dati.get('predizione', '')
                
                # Raccomandazioni ad alta confidenza (>70%)
                if confidenza > 70:
                    if nome_mercato == '1X2':
                        raccomandazioni.append({
                            'tipo': 'Forte',
                            'mercato': '1X2',
                            'scommessa': predizione,
                            'confidenza': confidenza,
                            'descrizione': f"Vittoria {predizione} molto probabile ({confidenza:.1f}%)"
                        })
                    elif nome_mercato == 'Over/Under 2.5':
                        raccomandazioni.append({
                            'tipo': 'Forte',
                            'mercato': 'Over/Under 2.5',
                            'scommessa': predizione,
                            'confidenza': confidenza,
                            'descrizione': f"{predizione} gol molto probabile ({confidenza:.1f}%)"
                        })
                    elif nome_mercato == 'BTTS':
                        valore = predizione  # Ora usa direttamente "Goal" o "NoGoal"
                        raccomandazioni.append({
                            'tipo': 'Forte',
                            'mercato': 'Goal/NoGoal',
                            'scommessa': valore,
                            'confidenza': confidenza,
                            'descrizione': f"Entrambe le squadre {('segneranno' if valore == 'Goal' else 'non segneranno')} ({confidenza:.1f}%)"
                        })
                
                # Raccomandazioni medie (60-70%)
                elif confidenza > 60:
                    raccomandazioni.append({
                        'tipo': 'Media',
                        'mercato': nome_mercato,
                        'scommessa': predizione,
                        'confidenza': confidenza,
                        'descrizione': f"Buona opportunità per {predizione} ({confidenza:.1f}%)"
                    })
            
            # Aggiungi raccomandazioni di valore se non ce ne sono ad alta confidenza
            if not any(r['tipo'] == 'Forte' for r in raccomandazioni):
                # Cerca il mercato con la confidenza più alta
                miglior_mercato = None
                max_confidenza = 0
                
                for nome_mercato in mercati_keys:
                    dati = risultato.get(nome_mercato, {})
                    if not isinstance(dati, dict) or 'confidenza' not in dati:
                        continue
                        
                    confidenza = dati.get('confidenza', 0)
                    if confidenza <= 1:  # Se è in decimale, converte in percentuale
                        confidenza = confidenza * 100
                        
                    if confidenza > max_confidenza:
                        max_confidenza = confidenza
                        miglior_mercato = (nome_mercato, dati)
                
                if miglior_mercato and max_confidenza > 50:
                    nome, dati = miglior_mercato
                    raccomandazioni.append({
                        'tipo': 'Valore',
                        'mercato': nome,
                        'scommessa': dati.get('predizione', ''),
                        'confidenza': max_confidenza,
                        'descrizione': f"Miglior valore disponibile: {dati.get('predizione', '')} ({max_confidenza:.1f}%)"
                    })
            
            # Limita a massimo 3 raccomandazioni per chiarezza
            return sorted(raccomandazioni, key=lambda x: x['confidenza'], reverse=True)[:3]
            
        except Exception as e:
            print(f"Errore nella generazione delle raccomandazioni: {e}")
            return []

    def _predizione_statistica(self, squadra_casa, squadra_trasferta):
        """Predizione avanzata basata su statistiche storiche complete"""
        try:
            if self.df is None:
                return self._predizione_default()
            
            # Analizza dati storici completi
            casa_home = self.df[self.df['HomeTeam'] == squadra_casa]
            casa_away = self.df[self.df['AwayTeam'] == squadra_casa]
            trasferta_home = self.df[self.df['HomeTeam'] == squadra_trasferta]
            trasferta_away = self.df[self.df['AwayTeam'] == squadra_trasferta]
            
            # === STATISTICHE CASA ===
            if len(casa_home) > 0:
                # Performance in casa
                vittorie_casa_home = (casa_home['FTR'] == 'H').mean()
                pareggi_casa_home = (casa_home['FTR'] == 'D').mean()
                sconfitte_casa_home = (casa_home['FTR'] == 'A').mean()
                gol_fatti_casa_home = casa_home['FTHG'].mean()
                gol_subiti_casa_home = casa_home['FTAG'].mean()
                
                # Performance generale
                casa_totale = pd.concat([casa_home, casa_away])
                if len(casa_totale) > 0:
                    # Vittorie totali
                    vittorie_casa_tot = ((casa_home['FTR'] == 'H').sum() + (casa_away['FTR'] == 'A').sum()) / len(casa_totale)
                    # Gol totali
                    gol_fatti_casa_tot = (casa_home['FTHG'].sum() + casa_away['FTAG'].sum()) / len(casa_totale)
                    gol_subiti_casa_tot = (casa_home['FTAG'].sum() + casa_away['FTHG'].sum()) / len(casa_totale)
                else:
                    vittorie_casa_tot = vittorie_casa_home
                    gol_fatti_casa_tot = gol_fatti_casa_home
                    gol_subiti_casa_tot = gol_subiti_casa_home
            else:
                # Valori default per squadra casa
                vittorie_casa_home, pareggi_casa_home, sconfitte_casa_home = 0.50, 0.25, 0.25
                gol_fatti_casa_home, gol_subiti_casa_home = 1.5, 1.2
                vittorie_casa_tot, gol_fatti_casa_tot, gol_subiti_casa_tot = 0.45, 1.4, 1.3
            
            # === STATISTICHE TRASFERTA ===
            if len(trasferta_away) > 0:
                # Performance in trasferta
                vittorie_trasferta_away = (trasferta_away['FTR'] == 'A').mean()
                pareggi_trasferta_away = (trasferta_away['FTR'] == 'D').mean()
                sconfitte_trasferta_away = (trasferta_away['FTR'] == 'H').mean()
                gol_fatti_trasferta_away = trasferta_away['FTAG'].mean()
                gol_subiti_trasferta_away = trasferta_away['FTHG'].mean()
                
                # Performance generale
                trasferta_totale = pd.concat([trasferta_home, trasferta_away])
                if len(trasferta_totale) > 0:
                    # Vittorie totali
                    vittorie_trasferta_tot = ((trasferta_home['FTR'] == 'H').sum() + (trasferta_away['FTR'] == 'A').sum()) / len(trasferta_totale)
                    # Gol totali
                    gol_fatti_trasferta_tot = (trasferta_home['FTHG'].sum() + trasferta_away['FTAG'].sum()) / len(trasferta_totale)
                    gol_subiti_trasferta_tot = (trasferta_home['FTAG'].sum() + trasferta_away['FTHG'].sum()) / len(trasferta_totale)
                else:
                    vittorie_trasferta_tot = vittorie_trasferta_away
                    gol_fatti_trasferta_tot = gol_fatti_trasferta_away
                    gol_subiti_trasferta_tot = gol_subiti_trasferta_away
            else:
                # Valori default per squadra trasferta
                vittorie_trasferta_away, pareggi_trasferta_away, sconfitte_trasferta_away = 0.25, 0.25, 0.50
                gol_fatti_trasferta_away, gol_subiti_trasferta_away = 1.2, 1.5
                vittorie_trasferta_tot, gol_fatti_trasferta_tot, gol_subiti_trasferta_tot = 0.35, 1.3, 1.4
            
            # === CONFRONTI DIRETTI ===
            h2h_home = self.df[(self.df['HomeTeam'] == squadra_casa) & (self.df['AwayTeam'] == squadra_trasferta)]
            h2h_away = self.df[(self.df['HomeTeam'] == squadra_trasferta) & (self.df['AwayTeam'] == squadra_casa)]
            
            if len(h2h_home) > 0 or len(h2h_away) > 0:
                # Peso maggiore per i confronti diretti
                h2h_vittorie_casa = 0
                h2h_pareggi = 0
                h2h_vittorie_trasferta = 0
                h2h_partite = len(h2h_home) + len(h2h_away)
                
                if len(h2h_home) > 0:
                    h2h_vittorie_casa += (h2h_home['FTR'] == 'H').sum()
                    h2h_pareggi += (h2h_home['FTR'] == 'D').sum()
                    h2h_vittorie_trasferta += (h2h_home['FTR'] == 'A').sum()
                
                if len(h2h_away) > 0:
                    h2h_vittorie_casa += (h2h_away['FTR'] == 'A').sum()
                    h2h_pareggi += (h2h_away['FTR'] == 'D').sum()
                    h2h_vittorie_trasferta += (h2h_away['FTR'] == 'H').sum()
                
                # Percentuali H2H
                h2h_prob_casa = h2h_vittorie_casa / h2h_partite if h2h_partite > 0 else 0.45
                h2h_prob_pareggio = h2h_pareggi / h2h_partite if h2h_partite > 0 else 0.25
                h2h_prob_trasferta = h2h_vittorie_trasferta / h2h_partite if h2h_partite > 0 else 0.30
                
                peso_h2h = 0.3  # 30% peso ai confronti diretti
            else:
                h2h_prob_casa, h2h_prob_pareggio, h2h_prob_trasferta = 0.45, 0.25, 0.30
                peso_h2h = 0.0
            
            # === CALCOLO PROBABILITÀ FINALI ===
            # Combinazione intelligente di tutti i fattori
            fattore_casa = 1.10  # Leggero vantaggio casa (10%)
            
            # Probabilità base da performance specifica (casa/trasferta)
            prob_h_base = vittorie_casa_home * fattore_casa
            prob_a_base = vittorie_trasferta_away
            prob_d_base = (pareggi_casa_home + pareggi_trasferta_away) / 2
            
            # Aggiustamenti basati su forza generale
            forza_casa = (vittorie_casa_tot + gol_fatti_casa_tot - gol_subiti_casa_tot) / 3
            forza_trasferta = (vittorie_trasferta_tot + gol_fatti_trasferta_tot - gol_subiti_trasferta_tot) / 3
            
            differenza_forza = forza_casa - forza_trasferta
            
            # Applica differenza di forza
            if differenza_forza > 0.2:  # Casa molto più forte
                prob_h_base *= 1.15
                prob_a_base *= 0.85
            elif differenza_forza < -0.2:  # Trasferta molto più forte
                prob_h_base *= 0.85
                prob_a_base *= 1.15
            
            # Combina con H2H se disponibile
            if peso_h2h > 0:
                prob_h = prob_h_base * (1 - peso_h2h) + h2h_prob_casa * peso_h2h
                prob_d = prob_d_base * (1 - peso_h2h) + h2h_prob_pareggio * peso_h2h
                prob_a = prob_a_base * (1 - peso_h2h) + h2h_prob_trasferta * peso_h2h
            else:
                prob_h, prob_d, prob_a = prob_h_base, prob_d_base, prob_a_base
            
            # Normalizza probabilità
            total = prob_h + prob_d + prob_a
            if total > 0:
                prob_h, prob_d, prob_a = prob_h/total, prob_d/total, prob_a/total
            else:
                prob_h, prob_d, prob_a = 0.45, 0.25, 0.30
            
            # Determina predizione e confidenza
            probabilities = {'H': prob_h, 'D': prob_d, 'A': prob_a}
            predizione = max(probabilities, key=lambda x: probabilities[x])
            confidenza = probabilities[predizione]
            
            # Aumenta confidenza se c'è molto supporto dai dati
            partite_casa = len(casa_home)
            partite_trasferta = len(trasferta_away)
            partite_h2h = len(h2h_home) + len(h2h_away)
            
            # Bonus confidenza per dati abbondanti
            if partite_casa >= 10 and partite_trasferta >= 10:
                confidenza *= 1.1
            if partite_h2h >= 3:
                confidenza *= 1.05
            
            # Cap confidenza al 95%
            confidenza = min(confidenza, 0.95)
            
            print(f"🎯 Predizione statistica avanzata: {squadra_casa} vs {squadra_trasferta}")
            print(f"   Casa: {prob_h:.3f}, Pareggio: {prob_d:.3f}, Trasferta: {prob_a:.3f}")
            print(f"   Predizione: {predizione}, Confidenza: {confidenza:.1%}")
            
            return {
                'predizione': predizione,
                'probabilita': probabilities,
                'confidenza': confidenza
            }
            
        except Exception as e:
            logger.warning(f"Errore predizione statistica avanzata: {e}, uso default")
            return self._predizione_default()
    
    def _predizione_default(self) -> dict:
        """Predizione di default quando non ci sono dati"""
        return {
            'predizione': 'H',  # Leggero vantaggio casa
            'probabilita': {'H': 0.45, 'D': 0.27, 'A': 0.28},
            'confidenza': 0.45
        }
    
    def _analizza_statistiche_gol(self, squadra_casa: str, squadra_trasferta: str) -> tuple:
        """Analizza in dettaglio le statistiche sui gol delle squadre con tutti i dati storici"""
        if self.df is None:
            return self._simula_statistiche_gol(squadra_casa, squadra_trasferta)
            
        try:
            print(f"🏠 Analisi statistiche {squadra_casa} vs {squadra_trasferta}")
            
            # === ANALISI SQUADRA CASA ===
            # Tutte le partite in casa
            casa_home = self.df[self.df['HomeTeam'] == squadra_casa]
            # Tutte le partite (casa + trasferta) per forma generale
            casa_all = pd.concat([
                self.df[self.df['HomeTeam'] == squadra_casa],
                self.df[self.df['AwayTeam'] == squadra_casa]
            ])
            
            if len(casa_home) > 0:
                print(f"   📊 {squadra_casa}: trovate {len(casa_home)} partite in casa")
                
                # Statistiche dettagliate casa
                gol_segnati_casa = casa_home['FTHG'].mean()
                gol_subiti_casa = casa_home['FTAG'].mean()
                clean_sheet_casa = (casa_home['FTAG'] == 0).mean()
                over_15_casa = (casa_home['FTHG'] > 1.5).mean()
                over_25_casa = ((casa_home['FTHG'] + casa_home['FTAG']) > 2.5).mean()
                btts_casa = ((casa_home['FTHG'] > 0) & (casa_home['FTAG'] > 0)).mean()
                
                # Forma recente (ultime 5 partite in casa)
                casa_recenti = casa_home.tail(5)
                punti_casa_recenti = 0
                for _, partita in casa_recenti.iterrows():
                    if partita['FTR'] == 'H':
                        punti_casa_recenti += 3
                    elif partita['FTR'] == 'D':
                        punti_casa_recenti += 1
                
                punti_media_casa = punti_casa_recenti / len(casa_recenti) if len(casa_recenti) > 0 else 1.5
                vittorie_perc_casa = (casa_home['FTR'] == 'H').mean()
                pareggi_perc_casa = (casa_home['FTR'] == 'D').mean()
                sconfitte_perc_casa = (casa_home['FTR'] == 'A').mean()
                
                print(f"   📈 {squadra_casa}: punti={punti_media_casa:.1f}, gol_fatti={gol_segnati_casa:.1f}")
                
                stats_casa = {
                    'punti_media': punti_media_casa,
                    'gol_fatti_media': gol_segnati_casa,
                    'gol_subiti_media': gol_subiti_casa,
                    'clean_sheet_rate': clean_sheet_casa,
                    'over_15_rate': over_15_casa,
                    'over_25_rate': over_25_casa,
                    'btts_rate': btts_casa,
                    'vittorie_perc': vittorie_perc_casa,
                    'pareggi_perc': pareggi_perc_casa,
                    'sconfitte_perc': sconfitte_perc_casa,
                    'partite_totali': len(casa_home)
                }
            else:
                print(f"   ⚠️ Nessuna partita in casa trovata per {squadra_casa}, uso valori default")
                stats_casa = self._simula_statistiche_squadra(squadra_casa)
            
            # === ANALISI SQUADRA TRASFERTA ===
            # Tutte le partite in trasferta
            trasferta_away = self.df[self.df['AwayTeam'] == squadra_trasferta]
            # Tutte le partite per forma generale
            trasferta_all = pd.concat([
                self.df[self.df['HomeTeam'] == squadra_trasferta],
                self.df[self.df['AwayTeam'] == squadra_trasferta]
            ])
            
            if len(trasferta_away) > 0:
                print(f"   📊 {squadra_trasferta}: trovate {len(trasferta_away)} partite in trasferta")
                
                # Statistiche dettagliate trasferta
                gol_segnati_trasferta = trasferta_away['FTAG'].mean()
                gol_subiti_trasferta = trasferta_away['FTHG'].mean()
                clean_sheet_trasferta = (trasferta_away['FTHG'] == 0).mean()
                over_15_trasferta = (trasferta_away['FTAG'] > 1.5).mean()
                over_25_trasferta = ((trasferta_away['FTHG'] + trasferta_away['FTAG']) > 2.5).mean()
                btts_trasferta = ((trasferta_away['FTHG'] > 0) & (trasferta_away['FTAG'] > 0)).mean()
                
                # Forma recente (ultime 5 partite in trasferta)
                trasferta_recenti = trasferta_away.tail(5)
                punti_trasferta_recenti = 0
                for _, partita in trasferta_recenti.iterrows():
                    if partita['FTR'] == 'A':
                        punti_trasferta_recenti += 3
                    elif partita['FTR'] == 'D':
                        punti_trasferta_recenti += 1
                
                punti_media_trasferta = punti_trasferta_recenti / len(trasferta_recenti) if len(trasferta_recenti) > 0 else 1.0
                vittorie_perc_trasferta = (trasferta_away['FTR'] == 'A').mean()
                pareggi_perc_trasferta = (trasferta_away['FTR'] == 'D').mean()
                sconfitte_perc_trasferta = (trasferta_away['FTR'] == 'H').mean()
                
                print(f"   📈 {squadra_trasferta}: punti={punti_media_trasferta:.1f}, gol_fatti={gol_segnati_trasferta:.1f}")
                
                stats_trasferta = {
                    'punti_media': punti_media_trasferta,
                    'gol_fatti_media': gol_segnati_trasferta,
                    'gol_subiti_media': gol_subiti_trasferta,
                    'clean_sheet_rate': clean_sheet_trasferta,
                    'over_15_rate': over_15_trasferta,
                    'over_25_rate': over_25_trasferta,
                    'btts_rate': btts_trasferta,
                    'vittorie_perc': vittorie_perc_trasferta,
                    'pareggi_perc': pareggi_perc_trasferta,
                    'sconfitte_perc': sconfitte_perc_trasferta,
                    'partite_totali': len(trasferta_away)
                }
            else:
                print(f"   ⚠️ Nessuna partita in trasferta trovata per {squadra_trasferta}, uso valori default")
                stats_trasferta = self._simula_statistiche_squadra(squadra_trasferta)
            
            print(f"📊 Stats casa: {stats_casa}")
            print(f"📊 Stats trasferta: {stats_trasferta}")
            
            return stats_casa, stats_trasferta
            
        except Exception as e:
            logger.warning(f"Errore analisi statistiche gol: {e}")
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
        """Mercato Over/Under con soglie multiple (2.5 principale)"""
        # Calcola gol attesi
        gol_attesi = stats_casa['gol_fatti_media'] + stats_trasferta['gol_fatti_media']
        
        # Soglie multiple per over/under
        soglie = [1.5, 2.5, 3.5, 4.5]
        risultato = {}
        
        # Soglia principale (2.5)
        soglia_principale = 2.5
        if gol_attesi > soglia_principale + 0.3:
            predizione_principale = 'Over 2.5'
            prob_over_principale = min(0.85, 0.5 + (gol_attesi - soglia_principale) * 0.15)
        elif gol_attesi < soglia_principale - 0.3:
            predizione_principale = 'Under 2.5'
            prob_over_principale = max(0.15, 0.5 - (soglia_principale - gol_attesi) * 0.15)
        else:
            predizione_principale = 'Over 2.5' if gol_attesi >= soglia_principale else 'Under 2.5'
            prob_over_principale = 0.5 + (gol_attesi - soglia_principale) * 0.1
        
        prob_under_principale = 1 - prob_over_principale
        
        # Campi principali
        risultato['predizione'] = predizione_principale
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['gol_attesi'] = round(gol_attesi, 2)
        risultato['confidenza'] = round(abs(prob_over_principale - 0.5) * 2, 3)
        risultato['valore_scommessa'] = 'Alta' if abs(gol_attesi - soglia_principale) > 0.5 else 'Media'
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            if soglia == 1.5:
                prob_over = min(0.9, 0.3 + (gol_attesi / 4.0))
            elif soglia == 2.5:
                prob_over = prob_over_principale
            elif soglia == 3.5:
                prob_over = max(0.1, min(0.7, (gol_attesi - 2.0) / 3.0))
            else:  # 4.5
                prob_over = max(0.05, min(0.6, (gol_attesi - 2.5) / 4.0))
            
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato
    
    def _mercato_btts(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Goal/NoGoal (Both Teams To Score)"""
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
        
        predizione = 'Goal' if prob_btts_si > self.mercati_config['btts']['probabilita_minima'] else 'NoGoal'
        
        return {
            'predizione': predizione,
            'probabilita': {'Goal': prob_btts_si, 'NoGoal': prob_btts_no},
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
        diff_gol = stats_casa['gol_fatti_media'] - stats_trasferta['gol_fatti_media']
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
        gol_casa_attesi = stats_casa['gol_fatti_media']
        gol_trasferta_attesi = stats_trasferta['gol_fatti_media']
        
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
        """Simula statistiche realistiche per una squadra basate su valori tipici Serie A"""
        # Usa hash del nome per consistenza tra chiamate
        seed = hash(squadra) % 1000
        np.random.seed(seed)
        
        # Valori realistici basati su medie Serie A
        base_strength = np.random.uniform(0.3, 0.9)  # Forza generale della squadra
        
        # Calcola statistiche proporzionali alla forza
        gol_fatti_media = 1.0 + (base_strength * 1.2)  # Range 1.0 - 2.2
        gol_subiti_media = 2.0 - (base_strength * 0.8)  # Range 1.2 - 2.0 (inverso)
        
        punti_media = base_strength * 2.5  # Range 0.75 - 2.25 punti per partita
        
        # Percentuali realistiche
        vittorie_perc = 0.2 + (base_strength * 0.5)  # Range 20% - 70%
        pareggi_perc = 0.25 + (np.random.uniform(-0.05, 0.05))  # ~25% con variazione
        sconfitte_perc = 1.0 - vittorie_perc - pareggi_perc
        
        # Assicura che le percentuali sommino a 1.0
        total = vittorie_perc + pareggi_perc + sconfitte_perc
        vittorie_perc /= total
        pareggi_perc /= total
        sconfitte_perc /= total
        
        return {
            'punti_media': punti_media,
            'gol_fatti_media': gol_fatti_media,
            'gol_subiti_media': gol_subiti_media,
            'clean_sheet_rate': 0.1 + (base_strength * 0.3),  # Range 10% - 40%
            'over_15_rate': 0.3 + (base_strength * 0.4),  # Range 30% - 70%
            'over_25_rate': 0.4 + (np.random.uniform(-0.1, 0.2)),  # Range 30% - 60%
            'btts_rate': 0.45 + (np.random.uniform(-0.15, 0.15)),  # Range 30% - 60%
            'vittorie_perc': vittorie_perc,
            'pareggi_perc': pareggi_perc,
            'sconfitte_perc': sconfitte_perc,
            'partite_totali': 0  # Indica che sono dati simulati
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
    
    def _mercato_over_under_15(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Over/Under 1.5 con soglie multiple"""
        # Media gol combinata
        gol_casa = stats_casa.get('gol_fatti_media', 1.2)
        gol_trasferta = stats_trasferta.get('gol_fatti_media', 1.1)
        media_totale = gol_casa + gol_trasferta
        
        # Soglie multiple per over/under 1.5
        soglie = [0.5, 1.5, 2.5]
        risultato = {}
        
        # Soglia principale (1.5)
        soglia_principale = 1.5
        prob_over_principale = min(0.9, 0.3 + (media_totale / 4.0))
        prob_under_principale = 1 - prob_over_principale
        
        # Campi principali
        risultato['predizione'] = 'Over 1.5' if prob_over_principale > 0.6 else 'Under 1.5'
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['gol_attesi'] = round(media_totale, 2)
        risultato['confidenza'] = round(abs(prob_over_principale - 0.5) * 2, 3)
        risultato['valore_scommessa'] = 'Alta' if abs(prob_over_principale - 0.5) > 0.2 else 'Media'
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            if soglia == 0.5:
                prob_over = min(0.95, 0.6 + (media_totale / 5.0))
            elif soglia == 1.5:
                prob_over = prob_over_principale
            else:  # 2.5
                prob_over = max(0.2, min(0.8, (media_totale - 1.0) / 3.0))
            
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato
    
    def _mercato_over_under_35(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Over/Under 3.5 con soglie multiple"""
        # Media gol combinata
        gol_casa = stats_casa.get('gol_fatti_media', 1.2)
        gol_trasferta = stats_trasferta.get('gol_fatti_media', 1.1)
        media_totale = gol_casa + gol_trasferta
        
        # Soglie multiple per over/under 3.5
        soglie = [2.5, 3.5, 4.5, 5.5]
        risultato = {}
        
        # Soglia principale (3.5)
        soglia_principale = 3.5
        prob_over_principale = max(0.1, min(0.7, (media_totale - 2.0) / 3.0))
        prob_under_principale = 1 - prob_over_principale
        
        # Campi principali
        risultato['predizione'] = 'Over 3.5' if prob_over_principale > 0.5 else 'Under 3.5'
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['gol_attesi'] = round(media_totale, 2)
        risultato['confidenza'] = round(abs(prob_over_principale - 0.5) * 2, 3)
        risultato['valore_scommessa'] = 'Alta' if abs(prob_over_principale - 0.5) > 0.2 else 'Media'
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            if soglia == 2.5:
                prob_over = max(0.2, min(0.8, (media_totale - 1.5) / 2.5))
            elif soglia == 3.5:
                prob_over = prob_over_principale
            elif soglia == 4.5:
                prob_over = max(0.05, min(0.6, (media_totale - 2.5) / 4.0))
            else:  # 5.5
                prob_over = max(0.02, min(0.4, (media_totale - 3.0) / 5.0))
            
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato
    
    def _mercato_prima_squadra_gol(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Prima Squadra a Segnare"""
        # Analisi probabilità primo gol
        attacco_casa = stats_casa.get('gol_fatti_media', 1.2)
        attacco_trasferta = stats_trasferta.get('gol_fatti_media', 1.1)
        difesa_casa = stats_casa.get('gol_subiti_media', 1.1)
        difesa_trasferta = stats_trasferta.get('gol_subiti_media', 1.2)
        
        # Forza offensiva vs difensiva
        forza_casa = attacco_casa / max(0.5, difesa_trasferta)
        forza_trasferta = attacco_trasferta / max(0.5, difesa_casa)
        
        # Vantaggio casa per primo gol
        forza_casa *= 1.15  # Bonus casa
        
        # Probabilità relative
        totale_forza = forza_casa + forza_trasferta
        prob_casa = forza_casa / totale_forza
        prob_trasferta = forza_trasferta / totale_forza
        prob_nessun_gol = 0.05  # Piccola probabilità di 0-0
        
        # Normalizza
        prob_casa *= (1 - prob_nessun_gol)
        prob_trasferta *= (1 - prob_nessun_gol)
        
        predizione = 'Casa' if prob_casa > prob_trasferta else 'Trasferta'
        
        return {
            'predizione': predizione,
            'probabilita_casa': prob_casa,
            'probabilita_trasferta': prob_trasferta,
            'probabilita_nessun_gol': prob_nessun_gol,
            'confidenza': abs(max(prob_casa, prob_trasferta) - 0.5),
            'valore_scommessa': 'Alta' if abs(prob_casa - prob_trasferta) > 0.3 else 'Media'
        }
    
    def _mercato_clean_sheet(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Clean Sheet (Porta Inviolata)"""
        prob_minima = self.mercati_config['clean_sheet']['probabilita_minima']
        
        # Analisi difensive
        difesa_casa = 1 / max(0.5, stats_casa.get('gol_subiti_media', 1.1))
        difesa_trasferta = 1 / max(0.5, stats_trasferta.get('gol_subiti_media', 1.2))
        
        attacco_casa = stats_casa.get('gol_fatti_media', 1.2)
        attacco_trasferta = stats_trasferta.get('gol_fatti_media', 1.1)
        
        # Probabilità clean sheet
        prob_clean_casa = max(prob_minima, min(0.8, difesa_casa / (difesa_casa + attacco_trasferta)))
        prob_clean_trasferta = max(prob_minima, min(0.8, difesa_trasferta / (difesa_trasferta + attacco_casa)))
        
        # Raccomandazione
        if prob_clean_casa > prob_clean_trasferta and prob_clean_casa > 0.4:
            predizione = 'Casa Clean Sheet'
            confidenza = prob_clean_casa
        elif prob_clean_trasferta > 0.4:
            predizione = 'Trasferta Clean Sheet'
            confidenza = prob_clean_trasferta
        else:
            predizione = 'Entrambe Segnano'
            confidenza = 1 - max(prob_clean_casa, prob_clean_trasferta)
        
        return {
            'predizione': predizione,
            'probabilita_clean_casa': prob_clean_casa,
            'probabilita_clean_trasferta': prob_clean_trasferta,
            'confidenza': confidenza,
            'valore_scommessa': 'Alta' if confidenza > 0.6 else 'Media'
        }
    
    def _mercato_primo_tempo_1x2(self, predizione_base: dict, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Risultato Primo Tempo 1X2"""
        # Nel primo tempo i risultati sono più conservativi
        prob_1_full = predizione_base.get('probabilita_1', 0.4)
        prob_x_full = predizione_base.get('probabilita_x', 0.3)
        prob_2_full = predizione_base.get('probabilita_2', 0.3)
        
        # Aumenta probabilità pareggio nel primo tempo
        prob_x_primo = min(0.6, prob_x_full * 1.8)
        prob_1_primo = prob_1_full * (1 - (prob_x_primo - prob_x_full))
        prob_2_primo = prob_2_full * (1 - (prob_x_primo - prob_x_full))
        
        # Normalizza
        totale = prob_1_primo + prob_x_primo + prob_2_primo
        prob_1_primo /= totale
        prob_x_primo /= totale
        prob_2_primo /= totale
        
        # Trova predizione
        probs = {'1': prob_1_primo, 'X': prob_x_primo, '2': prob_2_primo}
        predizione = max(probs.keys(), key=lambda k: probs[k])
        
        return {
            'predizione': predizione,
            'probabilita_1': prob_1_primo,
            'probabilita_x': prob_x_primo,
            'probabilita_2': prob_2_primo,
            'confidenza': max(probs.values()),
            'valore_scommessa': 'Alta' if max(probs.values()) > 0.5 else 'Media'
        }
    
    def _mercato_primo_tempo_over_under(self, stats_casa: dict, stats_trasferta: dict) -> dict:
        """Mercato Over/Under Primo Tempo con soglie multiple"""
        # Nel primo tempo si segna meno
        gol_casa_primo = stats_casa.get('gol_fatti_media', 1.2) * 0.6  # 60% dei gol nel primo tempo
        gol_trasferta_primo = stats_trasferta.get('gol_fatti_media', 1.1) * 0.6
        
        media_primo_tempo = gol_casa_primo + gol_trasferta_primo
        
        # Soglie multiple per primo tempo
        soglie = [0.5, 1.5, 2.5]
        risultato = {}
        
        # Soglia principale (1.5 è la più comune per primo tempo)
        soglia_principale = 1.5
        prob_over_principale = max(0.1, min(0.8, (media_primo_tempo - 0.5) / 2.0))
        prob_under_principale = 1 - prob_over_principale
        
        # Campi principali
        risultato['predizione'] = 'Over 1.5 PT' if prob_over_principale > 0.5 else 'Under 1.5 PT'
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['confidenza'] = round(abs(prob_over_principale - 0.5) * 2, 3)
        risultato['gol_attesi'] = round(media_primo_tempo, 2)
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            # Calcolo specifico per ogni soglia
            if soglia == 0.5:
                prob_over = max(0.1, min(0.9, (media_primo_tempo - 0.2) / 1.5))
            elif soglia == 1.5:
                prob_over = prob_over_principale
            else:  # 2.5
                prob_over = max(0.05, min(0.7, (media_primo_tempo - 1.0) / 3.0))
            
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia} PT' if prob_over > 0.5 else f'Under {soglia} PT',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato

    def _mercato_cartellini_totali(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Mercato cartellini totali nella partita con soglie multiple"""
        try:
            # Analizza statistiche cartellini storiche
            stats_cartellini_casa = self._analizza_cartellini_squadra(squadra_casa)
            stats_cartellini_trasferta = self._analizza_cartellini_squadra(squadra_trasferta)
            
            # Media cartellini per squadra
            cartellini_casa_media = stats_cartellini_casa.get('cartellini_media', 2.5)
            cartellini_trasferta_media = stats_cartellini_trasferta.get('cartellini_media', 2.5)
            
            # Totale previsto
            cartellini_totali_previsti = cartellini_casa_media + cartellini_trasferta_media
            
            # Aggiustamenti per intensità partita
            if squadra_casa in ['Juventus', 'Inter', 'Milan', 'Roma', 'Napoli'] or \
               squadra_trasferta in ['Juventus', 'Inter', 'Milan', 'Roma', 'Napoli']:
                cartellini_totali_previsti *= 1.1  # Partite big = più intensità
            
            # Soglie multiple per cartellini
            soglie = [3.5, 4.5, 5.5, 6.5]
            risultato = {}
            
            # Soglia principale (3.5)
            soglia_principale = 3.5
            diff_principale = cartellini_totali_previsti - soglia_principale
            prob_over_principale = max(0.1, min(0.9, 0.5 + diff_principale * 0.15))
            prob_under_principale = 1 - prob_over_principale
            
            # Campi principali
            risultato['cartellini_attesi'] = round(cartellini_totali_previsti, 1)
            risultato['casa_previsti'] = round(cartellini_casa_media, 1)
            risultato['trasferta_previsti'] = round(cartellini_trasferta_media, 1)
            risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
            risultato['predizione'] = f'Over 3.5' if prob_over_principale > 0.5 else f'Under 3.5'
            risultato['confidenza'] = 0.7
            
            # Dettagli per tutte le soglie
            for soglia in soglie:
                diff = cartellini_totali_previsti - soglia
                
                if soglia == 3.5:
                    prob_over = prob_over_principale
                elif soglia == 4.5:
                    prob_over = max(0.05, min(0.8, 0.5 + diff * 0.12))
                elif soglia == 5.5:
                    prob_over = max(0.02, min(0.7, 0.5 + diff * 0.10))
                else:  # 6.5
                    prob_over = max(0.01, min(0.6, 0.5 + diff * 0.08))
                
                prob_under = 1 - prob_over
                
                risultato[f'over_{soglia}'] = {
                    'over': round(prob_over, 3),
                    'under': round(prob_under, 3),
                    'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                    'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                    'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
                }
            
            return risultato
            
        except Exception as e:
            # Fallback con valori medi Serie A e soglie multiple
            risultato = {
                'cartellini_attesi': 5.0,
                'casa_previsti': 2.5,
                'trasferta_previsti': 2.5,
                'probabilita': {'Over': 0.65, 'Under': 0.35},
                'predizione': 'Over 3.5',
                'confidenza': 0.5
            }
            
            # Soglie di fallback
            soglie_fallback = [3.5, 4.5, 5.5, 6.5]
            for soglia in soglie_fallback:
                if soglia == 3.5:
                    prob_over = 0.65
                elif soglia == 4.5:
                    prob_over = 0.50
                elif soglia == 5.5:
                    prob_over = 0.35
                else:  # 6.5
                    prob_over = 0.20
                
                prob_under = 1 - prob_over
                
                risultato[f'over_{soglia}'] = {
                    'over': round(prob_over, 3),
                    'under': round(prob_under, 3),
                    'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                    'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                    'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
                }
            
            return risultato

    def _mercato_cartellini_over_under(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Mercato Over/Under cartellini"""
        cartellini_stats = self._mercato_cartellini_totali(squadra_casa, squadra_trasferta)
        cartellini_previsti = cartellini_stats['cartellini_attesi']  # Usa il campo standardizzato
        
        # Soglie comuni per cartellini
        soglie = [3.5, 4.5, 5.5]
        risultato = {}
        
        # Soglia principale (4.5 è la più comune)
        soglia_principale = 4.5
        diff_principale = cartellini_previsti - soglia_principale
        prob_over_principale = max(0.1, min(0.9, 0.5 + diff_principale * 0.15))
        prob_under_principale = 1 - prob_over_principale
        
        # Predizione e confidenza principali
        predizione_principale = f'Over {soglia_principale}' if prob_over_principale > 0.5 else f'Under {soglia_principale}'
        confidenza_principale = max(prob_over_principale, prob_under_principale)
        
        # Aggiungi campi principali
        risultato['predizione'] = predizione_principale
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['confidenza'] = round(confidenza_principale, 3)
        risultato['cartellini_attesi'] = cartellini_previsti
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            diff = cartellini_previsti - soglia
            prob_over = max(0.1, min(0.9, 0.5 + diff * 0.15))
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato

    def _mercato_calci_angolo_totali(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Mercato calci d'angolo totali nella partita con soglie multiple"""
        try:
            # Analizza statistiche corner storiche
            stats_corner_casa = self._analizza_corner_squadra(squadra_casa)
            stats_corner_trasferta = self._analizza_corner_squadra(squadra_trasferta)
            
            # Media corner per squadra
            corner_casa_media = stats_corner_casa.get('corner_media', 5.5)
            corner_trasferta_media = stats_corner_trasferta.get('corner_media', 5.0)
            
            # Totale previsto
            corner_totali_previsti = corner_casa_media + corner_trasferta_media
            
            # Aggiustamenti per stile di gioco
            if squadra_casa in ['Atalanta', 'Napoli', 'Lazio']:  # Squadre offensive
                corner_totali_previsti *= 1.15
            elif squadra_casa in ['Inter', 'Juventus']:  # Squadre più controllate
                corner_totali_previsti *= 0.95
            
            # Soglie multiple per corner totali
            soglie = [8.5, 9.5, 10.5, 11.5, 12.5, 13.5]
            risultato = {
                'corner_attesi': round(corner_totali_previsti, 1),  # Campo standardizzato
                'casa_previsti': round(corner_casa_media, 1),
                'trasferta_previsti': round(corner_trasferta_media, 1),
                'confidenza': 0.75
            }
            
            # Soglia principale (10.5)
            soglia_principale = 10.5
            diff_principale = corner_totali_previsti - soglia_principale
            prob_over_principale = max(0.1, min(0.9, 0.5 + diff_principale * 0.12))
            prob_under_principale = 1 - prob_over_principale
            
            # Campi principali
            risultato['corner_attesi'] = round(corner_totali_previsti, 1)
            risultato['casa_previsti'] = round(corner_casa_media, 1)
            risultato['trasferta_previsti'] = round(corner_trasferta_media, 1)
            risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
            risultato['predizione'] = f'Over {soglia_principale}' if prob_over_principale > 0.5 else f'Under {soglia_principale}'
            risultato['confidenza'] = 0.6
            
            # Calcola probabilità per tutte le soglie
            for soglia in soglie:
                diff = corner_totali_previsti - soglia
                
                # Calcolo probabilità basato sulla distanza dalla soglia
                if soglia <= 9.5:
                    # Soglie basse: più facili da superare
                    prob_over = max(0.15, min(0.95, 0.65 + diff * 0.15))
                elif soglia <= 11.5:
                    # Soglie medie: probabilità standard
                    prob_over = max(0.10, min(0.90, 0.50 + diff * 0.12))
                else:
                    # Soglie alte: più difficili da superare
                    prob_over = max(0.05, min(0.85, 0.35 + diff * 0.10))
                
                prob_under = 1 - prob_over
                
                # Aggiungi i campi per questa soglia
                risultato[f'over_{soglia}'] = round(prob_over, 3)
                risultato[f'under_{soglia}'] = round(prob_under, 3)
                risultato[f'quota_over_{soglia}'] = round(1 / prob_over if prob_over > 0.05 else 20, 2)
                risultato[f'quota_under_{soglia}'] = round(1 / prob_under if prob_under > 0.05 else 20, 2)
            
            return risultato
            
        except Exception as e:
            # Fallback con valori medi Serie A e soglie multiple
            risultato = {
                'corner_attesi': 10.5,
                'casa_previsti': 5.5,
                'trasferta_previsti': 5.0,
                'probabilita': {'Over': 0.55, 'Under': 0.45},
                'predizione': 'Over 10.5',
                'confidenza': 0.6
            }
            
            # Aggiungi soglie multiple anche nel fallback
            soglie = [8.5, 9.5, 10.5, 11.5, 12.5, 13.5]
            for i, soglia in enumerate(soglie):
                prob_over = max(0.1, min(0.9, 0.7 - i * 0.1))
                prob_under = 1 - prob_over
                risultato[f'over_{soglia}'] = round(prob_over, 3)
                risultato[f'under_{soglia}'] = round(prob_under, 3)
                risultato[f'quota_over_{soglia}'] = round(1 / prob_over if prob_over > 0.05 else 20, 2)
                risultato[f'quota_under_{soglia}'] = round(1 / prob_under if prob_under > 0.05 else 20, 2)
            
            return risultato

    def _mercato_calci_angolo_over_under(self, squadra_casa: str, squadra_trasferta: str) -> dict:
        """Mercato Over/Under calci d'angolo con soglie multiple"""
        corner_stats = self._mercato_calci_angolo_totali(squadra_casa, squadra_trasferta)
        corner_previsti = corner_stats['corner_attesi']  # Usa il campo standardizzato
        
        # Soglie estese per corner (da 7.5 a 12.5)
        soglie = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5]
        risultato = {}
        
        # Soglia principale (10.5 è la più comune)
        soglia_principale = 10.5
        diff_principale = corner_previsti - soglia_principale
        prob_over_principale = max(0.1, min(0.9, 0.5 + diff_principale * 0.12))
        prob_under_principale = 1 - prob_over_principale
        
        # Predizione e confidenza principali
        predizione_principale = f'Over {soglia_principale}' if prob_over_principale > 0.5 else f'Under {soglia_principale}'
        confidenza_principale = max(prob_over_principale, prob_under_principale)
        
        # Aggiungi campi principali
        risultato['predizione'] = predizione_principale
        risultato['probabilita'] = {'Over': round(prob_over_principale, 3), 'Under': round(prob_under_principale, 3)}
        risultato['confidenza'] = round(confidenza_principale, 3)
        risultato['corner_attesi'] = round(corner_previsti, 2)
        risultato['valore_scommessa'] = 'Alta' if abs(prob_over_principale - 0.5) > 0.2 else 'Media'
        
        # Dettagli per tutte le soglie
        for soglia in soglie:
            diff = corner_previsti - soglia
            # Calcolo probabilità adattato per corner (più variabilità)
            if soglia <= 8.5:
                prob_over = min(0.95, 0.8 + (corner_previsti - 8) / 8.0)
            elif soglia <= 10.5:
                prob_over = max(0.1, min(0.9, 0.5 + diff * 0.12))
            else:  # soglie > 10.5
                prob_over = max(0.05, min(0.8, (corner_previsti - 9) / 8.0))
            
            prob_under = 1 - prob_over
            
            risultato[f'over_{soglia}'] = {
                'over': round(prob_over, 3),
                'under': round(prob_under, 3),
                'predizione': f'Over {soglia}' if prob_over > 0.5 else f'Under {soglia}',
                'quota_stimata_over': round(1 / prob_over if prob_over > 0.1 else 10, 2),
                'quota_stimata_under': round(1 / prob_under if prob_under > 0.1 else 10, 2)
            }
        
        return risultato

    def _analizza_cartellini_squadra(self, squadra: str) -> dict:
        """Analizza statistiche cartellini di una squadra"""
        try:
            if self.df is None:
                raise ValueError("Dataset non disponibile")
            
            # Filtra partite della squadra nella stagione corrente
            df_work = self.df.copy()
            if 'Date' in df_work.columns:
                df_work['Date'] = pd.to_datetime(df_work['Date'], errors='coerce')
                df_stagione = df_work[df_work['Date'] >= '2025-08-01']
            else:
                df_stagione = df_work
            
            partite_squadra = df_stagione[
                (df_stagione['HomeTeam'] == squadra) | 
                (df_stagione['AwayTeam'] == squadra)
            ]
            
            if len(partite_squadra) > 0:
                # Calcola media cartellini (simulata - in assenza di dati reali)
                # In un dataset reale avresti colonne come 'HY', 'AY', 'HR', 'AR'
                cartellini_media = 2.3 + np.random.normal(0, 0.3)  # Valore medio Serie A
                cartellini_media = max(1.0, min(4.0, cartellini_media))
            else:
                cartellini_media = 2.5  # Default
            
            return {
                'cartellini_media': cartellini_media,
                'partite_analizzate': len(partite_squadra)
            }
            
        except Exception as e:
            return {
                'cartellini_media': 2.5,
                'partite_analizzate': 0
            }

    def _analizza_corner_squadra(self, squadra: str) -> dict:
        """Analizza statistiche corner di una squadra"""
        try:
            if self.df is None:
                raise ValueError("Dataset non disponibile")
            
            # Filtra partite della squadra nella stagione corrente
            df_work = self.df.copy()
            if 'Date' in df_work.columns:
                df_work['Date'] = pd.to_datetime(df_work['Date'], errors='coerce')
                df_stagione = df_work[df_work['Date'] >= '2025-08-01']
            else:
                df_stagione = df_work
            
            partite_squadra = df_stagione[
                (df_stagione['HomeTeam'] == squadra) | 
                (df_stagione['AwayTeam'] == squadra)
            ]
            
            if len(partite_squadra) > 0:
                # Calcola media corner (simulata - in assenza di dati reali)
                # In un dataset reale avresti colonne come 'HC', 'AC' per corner casa/trasferta
                
                # Squadre offensive tendono ad avere più corner
                if squadra in ['Atalanta', 'Napoli', 'Lazio', 'Roma']:
                    corner_base = 5.8
                elif squadra in ['Inter', 'Milan', 'Juventus']:
                    corner_base = 5.3
                else:
                    corner_base = 5.0
                
                corner_media = corner_base + np.random.normal(0, 0.5)
                corner_media = max(3.0, min(8.0, corner_media))
            else:
                corner_media = 5.2  # Default
            
            return {
                'corner_media': corner_media,
                'partite_analizzate': len(partite_squadra)
            }
            
        except Exception as e:
            return {
                'corner_media': 5.2,
                'partite_analizzate': 0
            }