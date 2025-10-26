import pandas as pd
import numpy as np
from scripts.modelli_predittivi import PronosticiCalculator
from scripts.feature_engineering import FeatureEngineer
import os
from datetime import datetime, timedelta

class SistemaPronosticiEnhanced:
    def __init__(self):
        self.calculator = PronosticiCalculator()
        self.feature_engineer = None  # Inizializzato dopo il caricamento dati
        self.df_features = None
        self.df_completo = None
        self.squadre_disponibili = []
        
    def inizializza(self):
        """Inizializza il sistema caricando modelli e dati"""
        print("🏆 Inizializzazione Sistema Pronostici Enhanced...")
        
        # Carica modelli
        if os.path.exists('models/metadata.pkl'):
            self.calculator.carica_modelli()
            print("✅ Modelli caricati con successo")
        else:
            print("❌ Modelli non trovati. Esegui prima modelli_predittivi.py")
            return False
        
        # Carica dataset completo per feature engineering
        if os.path.exists('data/dataset_pulito.csv'):
            self.df_completo = pd.read_csv('data/dataset_pulito.csv')
            self.df_completo['Date'] = pd.to_datetime(self.df_completo['Date'])
            self.feature_engineer = FeatureEngineer(self.df_completo)
            print(f"✅ Dataset completo caricato: {len(self.df_completo)} partite")
        else:
            print("❌ Dataset pulito non trovato")
            return False
        
        # Carica dataset features per squadre disponibili
        if os.path.exists('data/dataset_features.csv'):
            self.df_features = pd.read_csv('data/dataset_features.csv')
            self.df_features['Date'] = pd.to_datetime(self.df_features['Date'])
            print(f"✅ Dataset features caricato: {len(self.df_features)} partite")
        else:
            print("❌ Dataset features non trovato")
            return False
        
        # Lista squadre disponibili
        squadre_casa = set(self.df_completo['HomeTeam'].unique())
        squadre_trasferta = set(self.df_completo['AwayTeam'].unique())
        self.squadre_disponibili = sorted(squadre_casa.union(squadre_trasferta))
        print(f"✅ {len(self.squadre_disponibili)} squadre disponibili")
        
        return True
    
    def crea_features_complete_predizione(self, squadra_casa, squadra_trasferta, data_predizione=None):
        """Crea tutte le 32 features necessarie per la predizione"""
        if data_predizione is None:
            data_predizione = datetime.now()
        
        # Usa il feature engineer per creare features complete
        features = {}
        
        # Verifica che feature_engineer sia inizializzato
        if self.feature_engineer is None:
            print("❌ Feature engineer non inizializzato")
            return None
        
        # 1. Forma generale squadre (ultimi 5 match)
        forma_casa = self.feature_engineer.calcola_forma_recente(squadra_casa, data_predizione, 5)
        forma_trasferta = self.feature_engineer.calcola_forma_recente(squadra_trasferta, data_predizione, 5)
        
        features.update({
            'casa_forma_punti': forma_casa['punti'],
            'casa_forma_media_punti': forma_casa['media_punti'],
            'casa_forma_gol_fatti': forma_casa['gol_fatti'],
            'casa_forma_gol_subiti': forma_casa['gol_subiti'],
            'casa_forma_media_gol_fatti': forma_casa['media_gol_fatti'],
            'casa_forma_media_gol_subiti': forma_casa['media_gol_subiti'],
        })
        
        features.update({
            'trasferta_forma_punti': forma_trasferta['punti'],
            'trasferta_forma_media_punti': forma_trasferta['media_punti'],
            'trasferta_forma_gol_fatti': forma_trasferta['gol_fatti'],
            'trasferta_forma_gol_subiti': forma_trasferta['gol_subiti'],
            'trasferta_forma_media_gol_fatti': forma_trasferta['media_gol_fatti'],
            'trasferta_forma_media_gol_subiti': forma_trasferta['media_gol_subiti'],
        })
        
        # 2. Performance casa/trasferta specifiche
        if self.feature_engineer is None:
            print("❌ Feature engineer non inizializzato")
            return None
            
        casa_home = self.feature_engineer.calcola_performance_casa_trasferta(squadra_casa, data_predizione, casa=True, n_partite=10)
        trasferta_away = self.feature_engineer.calcola_performance_casa_trasferta(squadra_trasferta, data_predizione, casa=False, n_partite=10)
        
        features.update({
            'casa_home_punti': casa_home['punti'],
            'casa_home_media_punti': casa_home['media_punti'],
            'casa_home_gol_fatti': casa_home['gol_fatti'],
            'casa_home_gol_subiti': casa_home['gol_subiti'],
            'casa_home_media_gol_fatti': casa_home['media_gol_fatti'],
            'casa_home_media_gol_subiti': casa_home['media_gol_subiti'],
        })
        
        features.update({
            'trasferta_away_punti': trasferta_away['punti'],
            'trasferta_away_media_punti': trasferta_away['media_punti'],
            'trasferta_away_gol_fatti': trasferta_away['gol_fatti'],
            'trasferta_away_gol_subiti': trasferta_away['gol_subiti'],
            'trasferta_away_media_gol_fatti': trasferta_away['media_gol_fatti'],
            'trasferta_away_media_gol_subiti': trasferta_away['media_gol_subiti'],
        })
        
        # 3. Head to head
        if self.feature_engineer is None:
            print("❌ Feature engineer non inizializzato")
            return None
            
        h2h = self.feature_engineer.calcola_head_to_head(squadra_casa, squadra_trasferta, data_predizione)
        features.update({
            'h2h_vittorie_casa': h2h['vittorie_casa'],
            'h2h_vittorie_trasferta': h2h['vittorie_trasferta'],
            'h2h_pareggi': h2h['pareggi'],
            'h2h_partite': h2h['partite'],
        })
        
        # 4. Features derivate
        features['differenza_forma_punti'] = features['casa_forma_media_punti'] - features['trasferta_forma_media_punti']
        features['differenza_attacco'] = features['casa_forma_media_gol_fatti'] - features['trasferta_forma_media_gol_fatti']
        features['differenza_difesa'] = features['trasferta_forma_media_gol_subiti'] - features['casa_forma_media_gol_subiti']
        features['casa_home_vs_trasferta_away_punti'] = features['casa_home_media_punti'] - features['trasferta_away_media_punti']
        
        return features
    
    def predici_partita_enhanced(self, squadra_casa, squadra_trasferta):
        """Predizione enhanced con tutte le 32 features"""
        print(f"\n🎯 PREDIZIONE ENHANCED: {squadra_casa} vs {squadra_trasferta}")
        print("="*60)
        
        try:
            # Crea features complete
            features = self.crea_features_complete_predizione(squadra_casa, squadra_trasferta)
            
            # Converte in DataFrame con ordine corretto delle colonne
            feature_names = [
                'casa_forma_punti', 'casa_forma_media_punti', 'casa_forma_gol_fatti', 
                'casa_forma_gol_subiti', 'casa_forma_media_gol_fatti', 'casa_forma_media_gol_subiti',
                'casa_home_punti', 'casa_home_media_punti', 'casa_home_gol_fatti', 
                'casa_home_gol_subiti', 'casa_home_media_gol_fatti', 'casa_home_media_gol_subiti',
                'trasferta_forma_punti', 'trasferta_forma_media_punti', 'trasferta_forma_gol_fatti',
                'trasferta_forma_gol_subiti', 'trasferta_forma_media_gol_fatti', 'trasferta_forma_media_gol_subiti',
                'trasferta_away_punti', 'trasferta_away_media_punti', 'trasferta_away_gol_fatti',
                'trasferta_away_gol_subiti', 'trasferta_away_media_gol_fatti', 'trasferta_away_media_gol_subiti',
                'h2h_vittorie_casa', 'h2h_vittorie_trasferta', 'h2h_pareggi', 'h2h_partite',
                'differenza_forma_punti', 'differenza_attacco', 'differenza_difesa', 'casa_home_vs_trasferta_away_punti'
            ]
            
            # Verifica che features sia stato inizializzato
            if features is None:
                print("❌ Features non inizializzate")
                return None, None
            
            # Verifica che abbiamo tutte le features
            missing_features = [f for f in feature_names if f not in features]
            if missing_features:
                print(f"❌ Features mancanti: {missing_features}")
                return None, None
            
            # Crea DataFrame
            X = pd.DataFrame([features], columns=feature_names)
            print(f"✅ Features create: {X.shape[1]} features complete")
            
            # Predizione con il modello
            pred, prob = self.calculator.predici_partita_con_features(X)
            
            if pred and prob:
                # Mappa risultati
                risultato_map = {'H': 'Casa', 'A': 'Trasferta', 'D': 'Pareggio'}
                pred_str = pred[0] if isinstance(pred, list) else str(pred)
                
                print(f"\n🎯 RISULTATO ENHANCED:")
                print(f"   Predizione: {risultato_map.get(pred_str, pred_str)}")
                
                if isinstance(prob, dict):
                    max_conf = max(prob.values()) * 100
                    print(f"   Confidenza: {max_conf:.1f}%")
                    print(f"   Probabilità dettagliate:")
                    for esito, p in prob.items():
                        print(f"     {risultato_map.get(esito, esito)}: {p*100:.1f}%")
                
                # Suggerimenti enhanced
                self.genera_suggerimenti_enhanced(features, prob)
                
                return pred_str, prob
            else:
                print("❌ Predizione fallita")
                return None, None
                
        except Exception as e:
            print(f"❌ Errore nella predizione enhanced: {e}")
            return None, None
    
    def genera_suggerimenti_enhanced(self, features, prob):
        """Genera suggerimenti avanzati basati sulle features"""
        print(f"\n💡 SUGGERIMENTI ENHANCED:")
        
        # Analisi forma
        diff_forma = features['differenza_forma_punti']
        if abs(diff_forma) > 1.0:
            squadra_favorita = "Casa" if diff_forma > 0 else "Trasferta"
            print(f"   📈 {squadra_favorita} in forma migliore (diff: {diff_forma:.1f})")
        
        # Analisi attacco vs difesa
        diff_attacco = features['differenza_attacco']
        diff_difesa = features['differenza_difesa']
        
        if diff_attacco > 0.5:
            print(f"   ⚽ Casa ha attacco più forte (+{diff_attacco:.1f} gol/partita)")
        elif diff_attacco < -0.5:
            print(f"   ⚽ Trasferta ha attacco più forte ({diff_attacco:.1f} gol/partita)")
        
        if diff_difesa > 0.5:
            print(f"   🛡️ Casa ha difesa più solida (+{diff_difesa:.1f})")
        elif diff_difesa < -0.5:
            print(f"   🛡️ Trasferta ha difesa più solida ({abs(diff_difesa):.1f})")
        
        # Suggerimenti goal based
        gol_casa_attesi = features['casa_forma_media_gol_fatti']
        gol_trasferta_attesi = features['trasferta_forma_media_gol_fatti']
        totale_gol_attesi = gol_casa_attesi + gol_trasferta_attesi
        
        if totale_gol_attesi > 2.5:
            print(f"   🎯 Possibile Over 2.5 (attesi {totale_gol_attesi:.1f} gol)")
        elif totale_gol_attesi < 2.0:
            print(f"   🎯 Possibile Under 2.5 (attesi {totale_gol_attesi:.1f} gol)")
        
        # BTTS analysis
        if gol_casa_attesi > 0.8 and gol_trasferta_attesi > 0.8:
            print(f"   ⚽ Possibile Goal (entrambe segnano mediamente)")
        elif gol_casa_attesi < 0.7 or gol_trasferta_attesi < 0.7:
            print(f"   🚫 Possibile NoGoal (una squadra segna poco)")
        
        # H2H insights
        if features['h2h_partite'] > 0:
            casa_win_rate = features['h2h_vittorie_casa'] / features['h2h_partite']
            if casa_win_rate > 0.6:
                print(f"   📊 Casa domina negli scontri diretti ({casa_win_rate*100:.0f}%)")
            elif casa_win_rate < 0.3:
                print(f"   📊 Trasferta domina negli scontri diretti ({(1-casa_win_rate)*100:.0f}%)")

def get_forma_squadre_enhanced(squadra):
    """Funzione di utilità per ottenere forma squadra enhanced"""
    sistema = SistemaPronosticiEnhanced()
    if sistema.inizializza():
        if sistema.feature_engineer:
            forma = sistema.feature_engineer.calcola_forma_recente(squadra, datetime.now(), 5)
            forma['partite_analizzate'] = 5  # Per compatibilità
            return forma
    return None

if __name__ == "__main__":
    sistema = SistemaPronosticiEnhanced()
    
    if sistema.inizializza():
        print("\n🎯 TEST SISTEMA ENHANCED")
        print("="*50)
        
        # Test con alcune partite
        test_partite = [
            ('Juventus', 'Milan'),
            ('Inter', 'Roma'),
            ('Napoli', 'Lazio')
        ]
        
        for casa, trasferta in test_partite:
            pred, prob = sistema.predici_partita_enhanced(casa, trasferta)
            if pred:
                print(f"✅ Test {casa} vs {trasferta}: OK")
            else:
                print(f"❌ Test {casa} vs {trasferta}: FALLITO")
            print("-" * 50)
    else:
        print("❌ Inizializzazione fallita")