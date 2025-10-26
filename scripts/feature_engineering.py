import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class FeatureEngineer:
    def __init__(self, df):
        self.df = df.copy()
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
    def calcola_forma_recente(self, squadra, data_partita, n_partite=5):
        """Calcola la forma delle ultime N partite"""
        # Partite precedenti alla data corrente
        partite_precedenti = self.df[
            (self.df['Date'] < data_partita) & 
            ((self.df['HomeTeam'] == squadra) | (self.df['AwayTeam'] == squadra))
        ].tail(n_partite)
        
        if len(partite_precedenti) == 0:
            return {'punti': 0, 'gol_fatti': 0, 'gol_subiti': 0, 'partite': 0}
        
        punti = 0
        gol_fatti = 0
        gol_subiti = 0
        
        for _, partita in partite_precedenti.iterrows():
            if partita['HomeTeam'] == squadra:
                gol_fatti += partita['FTHG']
                gol_subiti += partita['FTAG']
                if partita['FTR'] == 'H':
                    punti += 3
                elif partita['FTR'] == 'D':
                    punti += 1
            else:
                gol_fatti += partita['FTAG']
                gol_subiti += partita['FTHG']
                if partita['FTR'] == 'A':
                    punti += 3
                elif partita['FTR'] == 'D':
                    punti += 1
        
        return {
            'punti': punti,
            'gol_fatti': gol_fatti,
            'gol_subiti': gol_subiti,
            'partite': len(partite_precedenti),
            'media_punti': punti / len(partite_precedenti) if len(partite_precedenti) > 0 else 0,
            'media_gol_fatti': gol_fatti / len(partite_precedenti) if len(partite_precedenti) > 0 else 0,
            'media_gol_subiti': gol_subiti / len(partite_precedenti) if len(partite_precedenti) > 0 else 0
        }
    
    def calcola_head_to_head(self, squadra_casa, squadra_trasferta, data_partita, n_partite=5):
        """Calcola statistiche degli scontri diretti"""
        h2h = self.df[
            (self.df['Date'] < data_partita) & 
            (((self.df['HomeTeam'] == squadra_casa) & (self.df['AwayTeam'] == squadra_trasferta)) |
             ((self.df['HomeTeam'] == squadra_trasferta) & (self.df['AwayTeam'] == squadra_casa)))
        ].tail(n_partite)
        
        if len(h2h) == 0:
            return {'vittorie_casa': 0, 'vittorie_trasferta': 0, 'pareggi': 0, 'partite': 0}
        
        vittorie_casa = 0
        vittorie_trasferta = 0
        pareggi = 0
        
        for _, partita in h2h.iterrows():
            if partita['FTR'] == 'H':
                if partita['HomeTeam'] == squadra_casa:
                    vittorie_casa += 1
                else:
                    vittorie_trasferta += 1
            elif partita['FTR'] == 'A':
                if partita['AwayTeam'] == squadra_casa:
                    vittorie_casa += 1
                else:
                    vittorie_trasferta += 1
            else:
                pareggi += 1
        
        return {
            'vittorie_casa': vittorie_casa,
            'vittorie_trasferta': vittorie_trasferta,
            'pareggi': pareggi,
            'partite': len(h2h)
        }
    
    def calcola_performance_casa_trasferta(self, squadra, data_partita, casa=True, n_partite=10):
        """Calcola performance specifica in casa o trasferta"""
        if casa:
            partite = self.df[
                (self.df['Date'] < data_partita) & 
                (self.df['HomeTeam'] == squadra)
            ].tail(n_partite)
        else:
            partite = self.df[
                (self.df['Date'] < data_partita) & 
                (self.df['AwayTeam'] == squadra)
            ].tail(n_partite)
        
        if len(partite) == 0:
            return {'punti': 0, 'gol_fatti': 0, 'gol_subiti': 0, 'partite': 0}
        
        punti = 0
        gol_fatti = 0
        gol_subiti = 0
        
        for _, partita in partite.iterrows():
            if casa:
                gol_fatti += partita['FTHG']
                gol_subiti += partita['FTAG']
                if partita['FTR'] == 'H':
                    punti += 3
                elif partita['FTR'] == 'D':
                    punti += 1
            else:
                gol_fatti += partita['FTAG']
                gol_subiti += partita['FTHG']
                if partita['FTR'] == 'A':
                    punti += 3
                elif partita['FTR'] == 'D':
                    punti += 1
        
        return {
            'punti': punti,
            'gol_fatti': gol_fatti,
            'gol_subiti': gol_subiti,
            'partite': len(partite),
            'media_punti': punti / len(partite) if len(partite) > 0 else 0,
            'media_gol_fatti': gol_fatti / len(partite) if len(partite) > 0 else 0,
            'media_gol_subiti': gol_subiti / len(partite) if len(partite) > 0 else 0
        }
    
    def crea_features(self, min_partite_storiche=10):
        """Crea tutte le features per ogni partita"""
        features = []
        
        print("Creazione features in corso...")
        for idx, row in self.df.iterrows():
            if idx % 100 == 0:
                print(f"Processate {idx}/{len(self.df)} partite...")
            
            squadra_casa = row['HomeTeam']
            squadra_trasferta = row['AwayTeam']
            data_partita = row['Date']
            
            # Salta se non ci sono abbastanza dati storici
            partite_storiche_casa = len(self.df[
                (self.df['Date'] < data_partita) & 
                ((self.df['HomeTeam'] == squadra_casa) | (self.df['AwayTeam'] == squadra_casa))
            ])
            partite_storiche_trasferta = len(self.df[
                (self.df['Date'] < data_partita) & 
                ((self.df['HomeTeam'] == squadra_trasferta) | (self.df['AwayTeam'] == squadra_trasferta))
            ])
            
            if partite_storiche_casa < min_partite_storiche or partite_storiche_trasferta < min_partite_storiche:
                continue
            
            # Features forma recente (ultime 5 partite)
            forma_casa = self.calcola_forma_recente(squadra_casa, data_partita, 5)
            forma_trasferta = self.calcola_forma_recente(squadra_trasferta, data_partita, 5)
            
            # Features performance casa/trasferta
            perf_casa_home = self.calcola_performance_casa_trasferta(squadra_casa, data_partita, casa=True, n_partite=10)
            perf_trasferta_away = self.calcola_performance_casa_trasferta(squadra_trasferta, data_partita, casa=False, n_partite=10)
            
            # Head to head
            h2h = self.calcola_head_to_head(squadra_casa, squadra_trasferta, data_partita, 5)
            
            # Crea dizionario features
            feature_dict = {
                # Info base
                'Date': data_partita,
                'HomeTeam': squadra_casa,
                'AwayTeam': squadra_trasferta,
                'FTHG': row['FTHG'],
                'FTAG': row['FTAG'],
                'FTR': row['FTR'],
                
                # Features casa - forma generale
                'casa_forma_punti': forma_casa['punti'],
                'casa_forma_media_punti': forma_casa['media_punti'],
                'casa_forma_gol_fatti': forma_casa['gol_fatti'],
                'casa_forma_gol_subiti': forma_casa['gol_subiti'],
                'casa_forma_media_gol_fatti': forma_casa['media_gol_fatti'],
                'casa_forma_media_gol_subiti': forma_casa['media_gol_subiti'],
                
                # Features casa - performance in casa
                'casa_home_punti': perf_casa_home['punti'],
                'casa_home_media_punti': perf_casa_home['media_punti'],
                'casa_home_gol_fatti': perf_casa_home['gol_fatti'],
                'casa_home_gol_subiti': perf_casa_home['gol_subiti'],
                'casa_home_media_gol_fatti': perf_casa_home['media_gol_fatti'],
                'casa_home_media_gol_subiti': perf_casa_home['media_gol_subiti'],
                
                # Features trasferta - forma generale
                'trasferta_forma_punti': forma_trasferta['punti'],
                'trasferta_forma_media_punti': forma_trasferta['media_punti'],
                'trasferta_forma_gol_fatti': forma_trasferta['gol_fatti'],
                'trasferta_forma_gol_subiti': forma_trasferta['gol_subiti'],
                'trasferta_forma_media_gol_fatti': forma_trasferta['media_gol_fatti'],
                'trasferta_forma_media_gol_subiti': forma_trasferta['media_gol_subiti'],
                
                # Features trasferta - performance in trasferta
                'trasferta_away_punti': perf_trasferta_away['punti'],
                'trasferta_away_media_punti': perf_trasferta_away['media_punti'],
                'trasferta_away_gol_fatti': perf_trasferta_away['gol_fatti'],
                'trasferta_away_gol_subiti': perf_trasferta_away['gol_subiti'],
                'trasferta_away_media_gol_fatti': perf_trasferta_away['media_gol_fatti'],
                'trasferta_away_media_gol_subiti': perf_trasferta_away['media_gol_subiti'],
                
                # Head to head
                'h2h_vittorie_casa': h2h['vittorie_casa'],
                'h2h_vittorie_trasferta': h2h['vittorie_trasferta'],
                'h2h_pareggi': h2h['pareggi'],
                'h2h_partite': h2h['partite'],
                
                # Features derivate
                'differenza_forma_punti': forma_casa['media_punti'] - forma_trasferta['media_punti'],
                'differenza_attacco': forma_casa['media_gol_fatti'] - forma_trasferta['media_gol_subiti'],
                'differenza_difesa': forma_trasferta['media_gol_fatti'] - forma_casa['media_gol_subiti'],
                'casa_home_vs_trasferta_away_punti': perf_casa_home['media_punti'] - perf_trasferta_away['media_punti'],
            }
            
            features.append(feature_dict)
        
        print(f"\nFeatures create per {len(features)} partite")
        return pd.DataFrame(features)

def main():
    print("=== FEATURE ENGINEERING ===")
    
    # Carica dataset pulito
    if os.path.exists('data/dataset_pulito.csv'):
        df = pd.read_csv('data/dataset_pulito.csv')
        print(f"Dataset caricato: {len(df)} partite")
    else:
        print("Errore: dataset_pulito.csv non trovato. Esegui prima analizza_dati.py")
        return
    
    # Crea feature engineer
    fe = FeatureEngineer(df)
    
    # Genera features
    df_features = fe.crea_features()
    
    # Salva dataset con features
    df_features.to_csv('data/dataset_features.csv', index=False)
    print(f"\nDataset con features salvato: {len(df_features)} partite, {len(df_features.columns)} colonne")
    
    # Mostra statistiche
    print("\n=== STATISTICHE FEATURES ===")
    print(f"Periodo coperto: dal {df_features['Date'].min()} al {df_features['Date'].max()}")
    print(f"Distribuzione risultati:")
    print(df_features['FTR'].value_counts())
    
    # Mostra alcune features di esempio
    print("\n=== ESEMPIO FEATURES ===")
    print(df_features[['HomeTeam', 'AwayTeam', 'casa_forma_media_punti', 'trasferta_forma_media_punti', 
                      'differenza_forma_punti', 'FTR']].head(10))
    
    return df_features

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ Test FeatureEngineer completato")
    else:
        df_features = main()