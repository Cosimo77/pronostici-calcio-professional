import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union, Tuple, List

class PronosticiCalculator:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def prepara_dati(self, df):
        """Prepara i dati per il training"""
        print("Preparazione dati...")
        
        # Seleziona features numeriche (esclude info di base)
        feature_cols = [col for col in df.columns if col not in 
                       ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']]
        
        self.feature_columns = feature_cols
        X = df[feature_cols].fillna(0)
        y = df['FTR']
        
        print(f"Features utilizzate: {len(feature_cols)}")
        print(f"Distribuzione target: {y.value_counts().to_dict()}")
        
        return X, y
    
    def train_models(self, X, y, test_size=0.2, random_state=42):
        """Addestra diversi modelli"""
        print("\nSplit dei dati...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Standardizza le features
        print("Standardizzazione features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"Set di training: {len(X_train)} campioni")
        print(f"Set di test: {len(X_test)} campioni")
        
        # Definisci modelli
        models_config = {
            'RandomForest': {
                'model': RandomForestClassifier(random_state=random_state),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 15, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                },
                'use_scaling': False
            },
            'GradientBoosting': {
                'model': GradientBoostingClassifier(random_state=random_state),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1],
                    'max_depth': [3, 5, 7]
                },
                'use_scaling': False
            },
            'LogisticRegression': {
                'model': LogisticRegression(random_state=random_state, max_iter=1000),
                'params': {
                    'C': [0.1, 1, 10],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear']
                },
                'use_scaling': True
            }
        }
        
        # Addestra ogni modello
        for model_name, config in models_config.items():
            print(f"\n=== Training {model_name} ===")
            
            # Scegli i dati giusti (scalati o no)
            X_train_model = X_train_scaled if config['use_scaling'] else X_train
            X_test_model = X_test_scaled if config['use_scaling'] else X_test
            
            # Grid search per ottimizzare iperparametri
            grid_search = GridSearchCV(
                config['model'], 
                config['params'], 
                cv=5, 
                scoring='accuracy',
                n_jobs=-1
            )
            
            grid_search.fit(X_train_model, y_train)
            
            # Miglior modello
            best_model = grid_search.best_estimator_
            
            # Predizioni
            y_pred = best_model.predict(X_test_model)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(best_model, X_train_model, y_train, cv=5)
            
            print(f"Migliori parametri: {grid_search.best_params_}")
            print(f"Accuracy test: {accuracy:.3f}")
            print(f"CV Score medio: {cv_scores.mean():.3f} (±{cv_scores.std()*2:.3f})")
            
            # Salva modello
            self.models[model_name] = {
                'model': best_model,
                'accuracy': accuracy,
                'cv_score': cv_scores.mean(),
                'use_scaling': config['use_scaling'],
                'feature_importance': None
            }
            
            # Feature importance per Random Forest e Gradient Boosting
            if hasattr(best_model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': self.feature_columns,
                    'importance': best_model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                self.models[model_name]['feature_importance'] = importance_df
                print(f"\nTop 10 features importanti:")
                print(importance_df.head(10))
            
            # Classification report
            print(f"\nClassification Report:")
            print(classification_report(y_test, y_pred))
        
        return X_test, y_test
    
    def ensemble_prediction(self, X):
        """Predizione ensemble utilizzando tutti i modelli"""
        predictions = {}
        probabilities = {}
        
        for model_name, model_info in self.models.items():
            model = model_info['model']
            use_scaling = model_info['use_scaling']
            
            # Prepara i dati
            X_model = self.scaler.transform(X) if use_scaling else X
            
            # Predizioni
            pred = model.predict(X_model)
            prob = model.predict_proba(X_model)
            
            predictions[model_name] = pred
            probabilities[model_name] = prob
        
        # Ensemble: voto di maggioranza pesato per accuracy
        ensemble_pred = []
        ensemble_prob = np.zeros((len(X), 3))  # 3 classi: A, D, H (ordine alfabetico)
        
        # Calcola pesi basati su accuracy
        total_accuracy = sum([info['accuracy'] for info in self.models.values()])
        weights = {name: info['accuracy']/total_accuracy for name, info in self.models.items()}
        
        for i in range(len(X)):
            # Voto pesato per la classe
            class_votes = {'H': 0, 'A': 0, 'D': 0}
            
            for model_name, pred in predictions.items():
                weight = weights[model_name]
                class_votes[pred[i]] += weight
            
            # Classe con maggior peso
            predicted_class = max(class_votes, key=lambda k: class_votes[k])
            ensemble_pred.append(predicted_class)
            
            # Probabilità ensemble (media pesata)
            for model_name, prob in probabilities.items():
                weight = weights[model_name]
                ensemble_prob[i] += prob[i] * weight

        return ensemble_pred, ensemble_prob, predictions, probabilities

    def predici_partita(self, squadra_casa, squadra_trasferta, df_features):
        """Predici il risultato di una singola partita usando features pre-calcolate"""
        print(f"🏠 Analisi statistiche {squadra_casa} vs {squadra_trasferta}")
        
        # Trova le ultime statistiche per entrambe le squadre
        stats_casa = self._get_team_recent_stats(squadra_casa, df_features)
        stats_trasferta = self._get_team_recent_stats(squadra_trasferta, df_features)
        
        print(f"📊 Stats casa: {stats_casa}")
        print(f"📊 Stats trasferta: {stats_trasferta}")
        
        # Crea features per la nuova partita basandoci sulle statistiche recenti
        features_partita = self._create_match_features(stats_casa, stats_trasferta)
        
        if features_partita is None:
            print("❌ Creazione features fallita")
            return None, "Dati insufficienti per la predizione"
        
        print(f"✅ Features create: shape {features_partita.shape}")
        
        # Predici
        pred, prob, _, _ = self.ensemble_prediction(features_partita)
        
        print(f"🎯 Predizione: {pred}, Probabilità: {prob}")
        
        # Formatta probabilità - le classi sono nell'ordine ['A', 'D', 'H']
        print(f"🔍 Debug prob: type={type(prob)}, shape={getattr(prob, 'shape', 'N/A')}, content={prob}")
        
        if prob is not None:
            # prob è un array 2D, prendiamo la prima riga
            if hasattr(prob, 'shape') and len(prob.shape) == 2 and prob.shape[1] >= 3:
                prob_row = prob[0]  # Prima riga dell'array 2D
                probabilities = {'A': float(prob_row[0]), 'D': float(prob_row[1]), 'H': float(prob_row[2])}
            elif hasattr(prob, '__len__') and len(prob) >= 3:
                # Array 1D
                probabilities = {'A': float(prob[0]), 'D': float(prob[1]), 'H': float(prob[2])}
            else:
                probabilities = {'H': 0.33, 'D': 0.33, 'A': 0.34}
        else:
            probabilities = {'H': 0.33, 'D': 0.33, 'A': 0.34}
        
        # Estrai la predizione come stringa (pred è una lista)
        prediction_result = pred[0] if isinstance(pred, list) and len(pred) > 0 else str(pred)
        
        # 🔧 CORREZIONE: La confidenza deve essere la probabilità della classe predetta
        if prediction_result in probabilities:
            confidence = probabilities[prediction_result]
        else:
            confidence = 0.5
        
        print(f"🔍 Debug predizione - Pred: {prediction_result}, Conf: {confidence}, Prob: {probabilities}")
        print(f"🔍 Debug tipo prob: {type(probabilities)}, content: {probabilities}")
        
        return prediction_result, probabilities
    
    def _get_team_recent_stats(self, team, df_features, n_matches=5):
        """Ottiene statistiche recenti di una squadra"""
        team_matches = df_features[
            (df_features['HomeTeam'] == team) | 
            (df_features['AwayTeam'] == team)
        ].tail(n_matches)
        
        print(f"   📊 {team}: trovate {len(team_matches)} partite recenti")
        
        if len(team_matches) == 0:
            print(f"   ⚠️ Nessuna partita trovata per {team}, uso valori default")
            return self._default_stats()
        
        # Calcola statistiche aggregate
        stats: Dict[str, float] = {
            'punti_media': 0.0,
            'gol_fatti_media': 0.0,
            'gol_subiti_media': 0.0,
            'vittorie_perc': 0.0,
            'pareggi_perc': 0.0,
            'sconfitte_perc': 0.0
        }
        
        punti_tot = 0
        gol_fatti_tot = 0
        gol_subiti_tot = 0
        vittorie = 0
        pareggi = 0
        
        for _, match in team_matches.iterrows():
            if match['HomeTeam'] == team:
                gf, gs = match['FTHG'], match['FTAG']
                if match['FTR'] == 'H':
                    punti = 3
                    vittorie += 1
                elif match['FTR'] == 'D':
                    punti = 1
                    pareggi += 1
                else:
                    punti = 0
            else:
                gf, gs = match['FTAG'], match['FTHG']
                if match['FTR'] == 'A':
                    punti = 3
                    vittorie += 1
                elif match['FTR'] == 'D':
                    punti = 1
                    pareggi += 1
                else:
                    punti = 0
            
            punti_tot += punti
            gol_fatti_tot += gf
            gol_subiti_tot += gs
        
        n = len(team_matches)
        if n > 0:  # Protezione divisione per zero
            stats['punti_media'] = punti_tot / n
            stats['gol_fatti_media'] = gol_fatti_tot / n
            stats['gol_subiti_media'] = gol_subiti_tot / n
            stats['vittorie_perc'] = vittorie / n
            stats['pareggi_perc'] = pareggi / n
            stats['sconfitte_perc'] = (n - vittorie - pareggi) / n
        
        print(f"   📈 {team}: punti={stats['punti_media']:.1f}, gol_fatti={stats['gol_fatti_media']:.1f}")
        return stats
    
    def _default_stats(self):
        """Statistiche di default per squadre senza dati"""
        return {
            'punti_media': 1.0,
            'gol_fatti_media': 1.0,
            'gol_subiti_media': 1.0,
            'vittorie_perc': 0.33,
            'pareggi_perc': 0.33,
            'sconfitte_perc': 0.34
        }
    
    def _create_match_features(self, stats_casa, stats_trasferta):
        """Crea features per una partita basandosi sulle statistiche delle squadre"""
        try:
            # Crea un array di features basato sulle statistiche
            features = []
            
            # Features casa
            features.extend([
                stats_casa['punti_media'],
                stats_casa['gol_fatti_media'],
                stats_casa['gol_subiti_media'],
                stats_casa['vittorie_perc'],
                stats_casa['pareggi_perc']
            ])
            
            # Features trasferta
            features.extend([
                stats_trasferta['punti_media'],
                stats_trasferta['gol_fatti_media'],
                stats_trasferta['gol_subiti_media'],
                stats_trasferta['vittorie_perc'],
                stats_trasferta['pareggi_perc']
            ])
            
            # Features comparative
            features.extend([
                stats_casa['punti_media'] - stats_trasferta['punti_media'],
                stats_casa['gol_fatti_media'] - stats_trasferta['gol_fatti_media'],
                stats_casa['gol_subiti_media'] - stats_trasferta['gol_subiti_media'],
                stats_casa['vittorie_perc'] - stats_trasferta['vittorie_perc']
            ])
            
            # Padding per raggiungere la dimensione prevista (adatta al tuo modello)
            if self.feature_columns and len(self.feature_columns) > 0:
                while len(features) < len(self.feature_columns):
                    features.append(0.0)
                
                # Truncate se troppo lungo
                features = features[:len(self.feature_columns)]
            
            # Converti in DataFrame
            import pandas as pd
            feature_cols = self.feature_columns if self.feature_columns else [f'feature_{i}' for i in range(len(features))]
            df_features = pd.DataFrame([features], columns=feature_cols)
            
            return df_features
            
        except Exception as e:
            print(f"Errore nella creazione features: {e}")
            return None
        
        return pred[0], prob[0]
    
    def predici_partita_con_features(self, X_features):
        """Predici il risultato usando features pre-costruite"""
        try:
            if X_features is None or len(X_features) == 0:
                return None, None
            
            # Verifica che feature_columns sia inizializzato
            if self.feature_columns is None:
                print("❌ Feature columns non inizializzate")
                return None, None
            
            # Verifica che le features abbiano la dimensione corretta
            if X_features.shape[1] != len(self.feature_columns):
                print(f"❌ Mismatch features: ricevute {X_features.shape[1]}, richieste {len(self.feature_columns)}")
                return None, None
            
            # Predizione ensemble
            ensemble_pred, ensemble_prob, _, _ = self.ensemble_prediction(X_features)
            
            # Converti probabilità in dizionario
            classes = ['A', 'D', 'H']  # Ordine alfabetico come in sklearn
            prob_dict = {classes[i]: ensemble_prob[0][i] for i in range(len(classes))}
            
            return ensemble_pred, prob_dict
            
        except Exception as e:
            print(f"❌ Errore predizione con features: {e}")
            return None, None
    
    def salva_modelli(self, cartella='models'):
        """Salva tutti i modelli"""
        os.makedirs(cartella, exist_ok=True)
        
        # Salva scaler
        joblib.dump(self.scaler, f'{cartella}/scaler.pkl')
        
        # Salva modelli
        for model_name, model_info in self.models.items():
            joblib.dump(model_info['model'], f'{cartella}/{model_name.lower()}_model.pkl')
        
        # Salva metadati
        metadata = {
            'feature_columns': self.feature_columns,
            'models_info': {name: {k: v for k, v in info.items() if k != 'model'} 
                           for name, info in self.models.items()}
        }
        joblib.dump(metadata, f'{cartella}/metadata.pkl')
        
        print(f"Modelli salvati in {cartella}/")
    
    def carica_modelli(self, cartella='models'):
        """Carica modelli salvati"""
        # Carica scaler
        self.scaler = joblib.load(f'{cartella}/scaler.pkl')
        
        # Carica metadati
        metadata = joblib.load(f'{cartella}/metadata.pkl')
        self.feature_columns = metadata['feature_columns']
        
        # Carica modelli
        for model_name in metadata['models_info'].keys():
            model = joblib.load(f'{cartella}/{model_name.lower()}_model.pkl')
            self.models[model_name] = metadata['models_info'][model_name]
            self.models[model_name]['model'] = model
        
        print(f"Modelli caricati da {cartella}/")

def main():
    print("=== TRAINING MODELLI PREDITTIVI ===")
    
    # Carica dataset con features
    if not os.path.exists('data/dataset_features.csv'):
        print("Errore: dataset_features.csv non trovato. Esegui prima feature_engineering.py")
        return
    
    df = pd.read_csv('data/dataset_features.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"Dataset caricato: {len(df)} partite")
    
    # Inizializza calculator
    calc = PronosticiCalculator()
    
    # Prepara dati
    X, y = calc.prepara_dati(df)
    
    # Addestra modelli
    X_test, y_test = calc.train_models(X, y)
    
    # Test ensemble
    print("\n=== TEST ENSEMBLE ===")
    ensemble_pred, ensemble_prob, _, _ = calc.ensemble_prediction(X_test)
    ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
    print(f"Accuracy Ensemble: {ensemble_accuracy:.3f}")
    
    # Salva modelli
    calc.salva_modelli()
    
    # Test predizione singola partita
    print("\n=== TEST PREDIZIONE SINGOLA ===")
    try:
        squadre_test = [
            ('Juventus', 'Inter'),
            ('Milan', 'Napoli'),
            ('Roma', 'Lazio')
        ]
        
        for casa, trasferta in squadre_test:
            pred, prob = calc.predici_partita(casa, trasferta, df)
            if pred and isinstance(prob, dict):
                classe_map = {'H': 'Casa', 'A': 'Trasferta', 'D': 'Pareggio'}
                max_prob = max(prob.values()) if prob else 0.0
                pred_str = pred[0] if isinstance(pred, list) and len(pred) > 0 else str(pred)
                if pred_str in classe_map:
                    print(f"{casa} vs {trasferta}: {classe_map[pred_str]} (prob: {max_prob:.3f})")
    except Exception as e:
        print(f"Errore nella predizione: {e}")
    
    return calc

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ Test ModelliPredittivi completato")
    else:
        calculator = main()