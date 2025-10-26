import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os

def crea_cache_features(df_features):
    """Crea una cache delle features pre-calcolate per velocizzare le predizioni"""
    print("🔧 Creazione cache features per predizioni veloci...")
    
    # Ultimi dati per ogni squadra
    cache = {}
    squadre = set(df_features['HomeTeam'].unique()).union(set(df_features['AwayTeam'].unique()))
    
    for squadra in squadre:
        # Trova l'ultima partita della squadra
        partite_squadra = df_features[
            (df_features['HomeTeam'] == squadra) | 
            (df_features['AwayTeam'] == squadra)
        ].sort_values('Date')
        
        if len(partite_squadra) > 0:
            ultima_partita = partite_squadra.iloc[-1]
            
            # Estrai features rilevanti
            if ultima_partita['HomeTeam'] == squadra:
                cache[squadra] = {
                    'ultima_data': ultima_partita['Date'],
                    'forma_punti': ultima_partita['casa_forma_punti'],
                    'forma_media_punti': ultima_partita['casa_forma_media_punti'],
                    'forma_gol_fatti': ultima_partita['casa_forma_gol_fatti'],
                    'forma_gol_subiti': ultima_partita['casa_forma_gol_subiti'],
                    'home_punti': ultima_partita['casa_home_punti'],
                    'home_media_punti': ultima_partita['casa_home_media_punti'],
                    'home_gol_fatti': ultima_partita['casa_home_gol_fatti'],
                    'home_gol_subiti': ultima_partita['casa_home_gol_subiti'],
                }
            else:
                cache[squadra] = {
                    'ultima_data': ultima_partita['Date'],
                    'forma_punti': ultima_partita['trasferta_forma_punti'],
                    'forma_media_punti': ultima_partita['trasferta_forma_media_punti'],
                    'forma_gol_fatti': ultima_partita['trasferta_forma_gol_fatti'],
                    'forma_gol_subiti': ultima_partita['trasferta_forma_gol_subiti'],
                    'away_punti': ultima_partita['trasferta_away_punti'],
                    'away_media_punti': ultima_partita['trasferta_away_media_punti'],
                    'away_gol_fatti': ultima_partita['trasferta_away_gol_fatti'],
                    'away_gol_subiti': ultima_partita['trasferta_away_gol_subiti'],
                }
    
    # Salva cache
    os.makedirs('cache', exist_ok=True)
    joblib.dump(cache, 'cache/features_cache.pkl')
    print(f"✅ Cache salvata per {len(cache)} squadre")
    
    return cache

def predizione_veloce(squadra_casa, squadra_trasferta, cache=None):
    """Predizione veloce utilizzando la cache"""
    if cache is None:
        if os.path.exists('cache/features_cache.pkl'):
            cache = joblib.load('cache/features_cache.pkl')
        else:
            print("❌ Cache non trovata. Usa predizione normale.")
            return None, None
    
    if squadra_casa not in cache or squadra_trasferta not in cache:
        print("❌ Squadre non trovate nella cache.")
        return None, None
    
    # Estrai features dalla cache
    casa_stats = cache[squadra_casa]
    trasferta_stats = cache[squadra_trasferta]
    
    # Crea feature vector semplificato (usando solo statistiche chiave)
    features = np.array([[
        casa_stats.get('forma_media_punti', 1.0),
        casa_stats.get('forma_gol_fatti', 5) / 5,  # Normalizza
        casa_stats.get('forma_gol_subiti', 5) / 5,
        casa_stats.get('home_media_punti', 1.0),
        casa_stats.get('home_gol_fatti', 5) / 5,
        casa_stats.get('home_gol_subiti', 5) / 5,
        trasferta_stats.get('forma_media_punti', 1.0),
        trasferta_stats.get('forma_gol_fatti', 5) / 5,
        trasferta_stats.get('forma_gol_subiti', 5) / 5,
        trasferta_stats.get('away_media_punti', 1.0),
        trasferta_stats.get('away_gol_fatti', 5) / 5,
        trasferta_stats.get('away_gol_subiti', 5) / 5,
        # Features derivate
        casa_stats.get('forma_media_punti', 1.0) - trasferta_stats.get('forma_media_punti', 1.0),
        (casa_stats.get('forma_gol_fatti', 5)/5) - (trasferta_stats.get('forma_gol_subiti', 5)/5),
        (trasferta_stats.get('forma_gol_fatti', 5)/5) - (casa_stats.get('forma_gol_subiti', 5)/5),
    ]])
    
    # Carica modello leggero (Random Forest)
    if os.path.exists('models/randomforest_model.pkl'):
        model = joblib.load('models/randomforest_model.pkl')
        
        # Predizione
        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0]
        
        return pred, prob
    
    return None, None

def main():
    """Crea cache per predizioni veloci"""
    print("🚀 Setup Cache Predizioni Veloci")
    
    # Carica dataset features
    if os.path.exists('data/dataset_features.csv'):
        df_features = pd.read_csv('data/dataset_features.csv')
        df_features['Date'] = pd.to_datetime(df_features['Date'])
        
        # Crea cache
        cache = crea_cache_features(df_features)
        
        # Test predizione veloce
        print("\n🧪 Test predizione veloce:")
        pred, prob = predizione_veloce('Juventus', 'Inter', cache)
        if pred:
            risultato_map = {'H': 'Casa', 'A': 'Trasferta', 'D': 'Pareggio'}
            print(f"Juventus vs Inter: {risultato_map[pred]} (prob: {prob.max():.1%})")
        
        print("\n✅ Cache setup completato!")
        
    else:
        print("❌ Dataset features non trovato. Esegui prima feature_engineering.py")

if __name__ == "__main__":
    main()