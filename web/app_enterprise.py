"""
Sistema Enterprise Pronostici Calcio
Architettura ML professionale con feature engineering avanzato
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import lightgbm as lgb
from flask import Flask, render_template, request, jsonify
import logging
import os
import sys
from datetime import datetime, timedelta
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configurazione logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enterprise_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enterprise_calcio_system_2025'

class EnterpriseMLEngine:
    """Engine ML Enterprise con algoritmi avanzati"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.validation_scores = {}
        self.is_trained = False
        
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Feature Engineering Ottimizzato"""
        logger.info("🔧 Avvio Feature Engineering Ottimizzato...")
        
        df_enhanced = df.copy()
        
        # Features temporali base
        if 'Date' in df.columns:
            df_enhanced['Date'] = pd.to_datetime(df_enhanced['Date'])
            df_enhanced = df_enhanced.sort_values('Date')
            df_enhanced['DayOfWeek'] = df_enhanced['Date'].dt.dayofweek
            df_enhanced['Month'] = df_enhanced['Date'].dt.month
            df_enhanced['IsWeekend'] = (df_enhanced['DayOfWeek'] >= 5).astype(int)
        else:
            df_enhanced['DayOfWeek'] = 0
            df_enhanced['Month'] = 1
            df_enhanced['IsWeekend'] = 0
        
        # Statistiche base squadre
        for team in df_enhanced['HomeTeam'].unique():
            # Statistiche in casa
            home_stats = df_enhanced[df_enhanced['HomeTeam'] == team]
            if len(home_stats) > 0:
                home_form = len(home_stats[home_stats['FTR'] == 'H']) / len(home_stats)
                home_goals_avg = home_stats['FTHG'].mean() if 'FTHG' in home_stats.columns else 1.5
                home_conceded_avg = home_stats['FTAG'].mean() if 'FTAG' in home_stats.columns else 1.2
                
                df_enhanced.loc[df_enhanced['HomeTeam'] == team, 'HomeForm'] = home_form
                df_enhanced.loc[df_enhanced['HomeTeam'] == team, 'HomeAvgGoalsFor'] = home_goals_avg
                df_enhanced.loc[df_enhanced['HomeTeam'] == team, 'HomeAvgGoalsAgainst'] = home_conceded_avg
            
            # Statistiche trasferta
            away_stats = df_enhanced[df_enhanced['AwayTeam'] == team]
            if len(away_stats) > 0:
                away_form = len(away_stats[away_stats['FTR'] == 'A']) / len(away_stats)
                away_goals_avg = away_stats['FTAG'].mean() if 'FTAG' in away_stats.columns else 1.2
                away_conceded_avg = away_stats['FTHG'].mean() if 'FTHG' in away_stats.columns else 1.5
                
                df_enhanced.loc[df_enhanced['AwayTeam'] == team, 'AwayForm'] = away_form
                df_enhanced.loc[df_enhanced['AwayTeam'] == team, 'AwayAvgGoalsFor'] = away_goals_avg
                df_enhanced.loc[df_enhanced['AwayTeam'] == team, 'AwayAvgGoalsAgainst'] = away_conceded_avg
        
        # Features derivate
        df_enhanced['GoalDifferential'] = df_enhanced.get('HomeAvgGoalsFor', 1.5) - df_enhanced.get('AwayAvgGoalsFor', 1.2)
        df_enhanced['FormDifferential'] = df_enhanced.get('HomeForm', 0.5) - df_enhanced.get('AwayForm', 0.3)
        
        # Riempi valori mancanti
        numeric_columns = df_enhanced.select_dtypes(include=[np.number]).columns
        df_enhanced[numeric_columns] = df_enhanced[numeric_columns].fillna(df_enhanced[numeric_columns].median())
        
        logger.info(f"✅ Feature Engineering completato: {len(df_enhanced.columns)} features")
        return df_enhanced
    
    def prepare_training_data(self, df: pd.DataFrame):
        """Prepara dati per training"""
        # Seleziona features numeriche
        feature_columns = [
            'FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC',
            'HF', 'AF', 'HY', 'AY', 'HR', 'AR', 'DayOfWeek', 'Month', 'IsWeekend',
            'HomeForm', 'AwayForm', 'HomeAvgGoalsFor', 'HomeAvgGoalsAgainst',
            'AwayAvgGoalsFor', 'AwayAvgGoalsAgainst', 'H2H_HomeAdvantage',
            'H2H_TotalMatches', 'GoalDifferential', 'FormDifferential'
        ]
        
        # Mantieni solo colonne esistenti
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].fillna(0)
        y = df['FTR'].map({'H': 2, 'D': 1, 'A': 0})  # 2=Home, 1=Draw, 0=Away
        
        return X, y, available_features
    
    def train_ensemble_models(self, df: pd.DataFrame):
        """Training ensemble di modelli ML avanzati"""
        logger.info("🚀 Avvio Training Ensemble ML...")
        
        # Feature engineering
        df_enhanced = self.engineer_features(df)
        X, y, feature_names = self.prepare_training_data(df_enhanced)
        
        logger.info(f"📊 Dataset: {len(X)} samples, {len(X.columns)} features")
        
        # Split temporale per validazione realistica
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Scaling dei dati
        self.scalers['standard'] = StandardScaler()
        X_scaled = self.scalers['standard'].fit_transform(X)
        
        # Modelli ensemble
        models_config = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                eval_metric='mlogloss'
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                verbose=-1
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000,
                multi_class='multinomial'
            )
        }
        
        # Training e validazione
        for name, model in models_config.items():
            logger.info(f"🔄 Training {name}...")
            
            # Cross-validation con split temporale
            if name == 'logistic_regression':
                scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='accuracy')
                model.fit(X_scaled, y)
            else:
                scores = cross_val_score(model, X, y, cv=tscv, scoring='accuracy')
                model.fit(X, y)
            
            self.models[name] = model
            self.validation_scores[name] = {
                'mean_accuracy': scores.mean(),
                'std_accuracy': scores.std(),
                'scores': scores.tolist()
            }
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance = dict(zip(feature_names, model.feature_importances_))
                self.feature_importance[name] = importance
            
            logger.info(f"✅ {name}: Accuracy {scores.mean():.3f} (±{scores.std():.3f})")
        
        # Ensemble meta-model
        self._create_ensemble_meta_model(X, X_scaled, y)
        
        self.is_trained = True
        self._save_models()
        
        logger.info("🏆 Training Ensemble completato!")
        
    def _create_ensemble_meta_model(self, X, X_scaled, y):
        """Crea meta-model per ensemble"""
        # Predizioni dei modelli base
        predictions = []
        
        for name, model in self.models.items():
            if name == 'logistic_regression':
                pred_proba = model.predict_proba(X_scaled)
            else:
                pred_proba = model.predict_proba(X)
            predictions.append(pred_proba)
        
        # Stack predictions
        stacked_predictions = np.hstack(predictions)
        
        # Meta-model
        meta_model = LogisticRegression(random_state=42, max_iter=1000)
        meta_model.fit(stacked_predictions, y)
        
        self.models['ensemble_meta'] = meta_model
        
    def predict_match_professional(self, home_team: str, away_team: str, recent_data: pd.DataFrame):
        """Predizione professionale con ensemble"""
        if not self.is_trained:
            raise ValueError("Modelli non ancora addestrati")
        
        # Simula dati per la partita
        match_data = self._create_match_features(home_team, away_team, recent_data)
        
        # Predizioni ensemble
        predictions = {}
        probabilities = {}
        
        for name, model in self.models.items():
            if name == 'ensemble_meta':
                continue
                
            if name == 'logistic_regression':
                X_match = self.scalers['standard'].transform(match_data)
                prob = model.predict_proba(X_match)[0]
            else:
                prob = model.predict_proba(match_data)[0]
            
            pred = np.argmax(prob)
            predictions[name] = pred
            probabilities[name] = prob
        
        # Ensemble finale
        ensemble_probs = self._calculate_ensemble_probability(match_data)
        ensemble_pred = np.argmax(ensemble_probs)
        
        # Converti in formato standard
        result_map = {0: 'A', 1: 'D', 2: 'H'}
        
        return {
            'ensemble_prediction': result_map[int(ensemble_pred)],
            'ensemble_probabilities': {
                'H': float(ensemble_probs[2]),
                'D': float(ensemble_probs[1]),
                'A': float(ensemble_probs[0])
            },
            'individual_models': {
                name: {
                    'prediction': result_map[pred],
                    'probabilities': {
                        'H': float(prob[2]),
                        'D': float(prob[1]),
                        'A': float(prob[0])
                    }
                }
                for name, (pred, prob) in zip(predictions.keys(), zip(predictions.values(), probabilities.values()))
            },
            'confidence': float(np.max(ensemble_probs)),
            'model_agreement': self._calculate_model_agreement(predictions)
        }
    
    def _create_match_features(self, home_team: str, away_team: str, recent_data: pd.DataFrame):
        """Crea features per match specifico"""
        # Statistiche recenti squadre
        home_recent = recent_data[recent_data['HomeTeam'] == home_team].tail(10)
        away_recent = recent_data[recent_data['AwayTeam'] == away_team].tail(10)
        
        # Features base
        features = {
            'FTHG': home_recent['FTHG'].mean() if len(home_recent) > 0 else 1.5,
            'FTAG': away_recent['FTAG'].mean() if len(away_recent) > 0 else 1.2,
            'HTHG': home_recent['HTHG'].mean() if len(home_recent) > 0 else 0.8,
            'HTAG': away_recent['HTAG'].mean() if len(away_recent) > 0 else 0.6,
            'HS': home_recent['HS'].mean() if len(home_recent) > 0 else 12,
            'AS': away_recent['AS'].mean() if len(away_recent) > 0 else 10,
            'HST': home_recent['HST'].mean() if len(home_recent) > 0 else 5,
            'AST': away_recent['AST'].mean() if len(away_recent) > 0 else 4,
            'HC': home_recent['HC'].mean() if len(home_recent) > 0 else 6,
            'AC': away_recent['AC'].mean() if len(away_recent) > 0 else 4,
            'HF': home_recent['HF'].mean() if len(home_recent) > 0 else 12,
            'AF': away_recent['AF'].mean() if len(away_recent) > 0 else 11,
            'HY': home_recent['HY'].mean() if len(home_recent) > 0 else 2,
            'AY': away_recent['AY'].mean() if len(away_recent) > 0 else 2,
            'HR': home_recent['HR'].mean() if len(home_recent) > 0 else 0.1,
            'AR': away_recent['AR'].mean() if len(away_recent) > 0 else 0.1,
            'DayOfWeek': datetime.now().weekday(),
            'Month': datetime.now().month,
            'IsWeekend': 1 if datetime.now().weekday() >= 5 else 0,
            'HomeForm': len(home_recent[home_recent['FTR'] == 'H']) / len(home_recent) if len(home_recent) > 0 else 0.5,
            'AwayForm': len(away_recent[away_recent['FTR'] == 'A']) / len(away_recent) if len(away_recent) > 0 else 0.3,
            'HomeAvgGoalsFor': home_recent['FTHG'].mean() if len(home_recent) > 0 else 1.5,
            'HomeAvgGoalsAgainst': home_recent['FTAG'].mean() if len(home_recent) > 0 else 1.2,
            'AwayAvgGoalsFor': away_recent['FTAG'].mean() if len(away_recent) > 0 else 1.2,
            'AwayAvgGoalsAgainst': away_recent['FTHG'].mean() if len(away_recent) > 0 else 1.5,
            'H2H_HomeAdvantage': 0.5,  # Valore neutro
            'H2H_TotalMatches': 5,
        }
        
        # Features derivate
        features['GoalDifferential'] = features['HomeAvgGoalsFor'] - features['AwayAvgGoalsFor']
        features['FormDifferential'] = features['HomeForm'] - features['AwayForm']
        
        return pd.DataFrame([features])
    
    def _calculate_ensemble_probability(self, match_data):
        """Calcola probabilità ensemble finale"""
        # Weighted voting basato su performance
        weights = {
            'random_forest': 0.25,
            'gradient_boosting': 0.20,
            'xgboost': 0.25,
            'lightgbm': 0.20,
            'logistic_regression': 0.10
        }
        
        ensemble_prob = np.zeros(3)
        
        for name, weight in weights.items():
            if name in self.models:
                if name == 'logistic_regression':
                    X_match = self.scalers['standard'].transform(match_data)
                    prob = self.models[name].predict_proba(X_match)[0]
                else:
                    prob = self.models[name].predict_proba(match_data)[0]
                
                ensemble_prob += weight * prob
        
        return ensemble_prob
    
    def _calculate_model_agreement(self, predictions):
        """Calcola accordo tra modelli"""
        pred_values = list(predictions.values())
        mode_pred = max(set(pred_values), key=pred_values.count)
        agreement = pred_values.count(mode_pred) / len(pred_values)
        return agreement
    
    def _save_models(self):
        """Salva modelli addestrati"""
        os.makedirs('models/enterprise', exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, f'models/enterprise/{name}.pkl')
        
        joblib.dump(self.scalers, 'models/enterprise/scalers.pkl')
        joblib.dump(self.validation_scores, 'models/enterprise/validation_scores.pkl')
        
        logger.info("💾 Modelli salvati in models/enterprise/")
    
    def load_models(self):
        """Carica modelli pre-addestrati"""
        try:
            model_files = [
                'random_forest.pkl', 'gradient_boosting.pkl', 'xgboost.pkl',
                'lightgbm.pkl', 'logistic_regression.pkl', 'ensemble_meta.pkl'
            ]
            
            for model_file in model_files:
                model_name = model_file.replace('.pkl', '')
                self.models[model_name] = joblib.load(f'models/enterprise/{model_file}')
            
            self.scalers = joblib.load('models/enterprise/scalers.pkl')
            self.validation_scores = joblib.load('models/enterprise/validation_scores.pkl')
            
            self.is_trained = True
            logger.info("✅ Modelli caricati da models/enterprise/")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Impossibile caricare modelli: {e}")
            return False

# Istanza globale
ml_engine = EnterpriseMLEngine()
system_initialized = False

def initialize_enterprise_system():
    """Inizializzazione sistema enterprise"""
    global system_initialized
    
    try:
        logger.info("🚀 Inizializzazione Sistema Enterprise...")
        
        # Carica dataset
        df = pd.read_csv('data/dataset_features.csv')
        logger.info(f"📊 Dataset caricato: {len(df)} partite")
        
        # Prova a caricare modelli esistenti
        if not ml_engine.load_models():
            logger.info("🔄 Modelli non trovati, avvio training...")
            ml_engine.train_ensemble_models(df)
        
        system_initialized = True
        logger.info("✅ Sistema Enterprise inizializzato")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione: {e}")
        return False

# ==================== API ENDPOINTS ====================

@app.route('/api/predict_enterprise', methods=['POST'])
def api_predict_enterprise():
    """API predizione enterprise"""
    if not system_initialized:
        return jsonify({'error': 'Sistema non inizializzato'}), 500
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dati JSON mancanti'}), 400
            
        home_team = data.get('squadra_casa')
        away_team = data.get('squadra_ospite')
        
        if not home_team or not away_team:
            return jsonify({'error': 'Squadre mancanti'}), 400
        
        # Carica dati recenti
        recent_data = pd.read_csv('data/dataset_features.csv')
        
        # Predizione enterprise
        result = ml_engine.predict_match_professional(home_team, away_team, recent_data)
        
        response = {
            'predizione_enterprise': result['ensemble_prediction'],
            'probabilita_ensemble': result['ensemble_probabilities'],
            'confidenza': result['confidence'],
            'accordo_modelli': result['model_agreement'],
            'modelli_individuali': result['individual_models'],
            'modalita': 'enterprise_ml',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Predizione Enterprise: {home_team} vs {away_team} → {result['ensemble_prediction']} ({result['confidence']:.3f})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Errore predizione enterprise: {e}")
        return jsonify({'error': f'Errore interno: {str(e)}'}), 500

@app.route('/api/model_performance')
def api_model_performance():
    """API performance modelli"""
    if not system_initialized:
        return jsonify({'error': 'Sistema non inizializzato'}), 500
    
    return jsonify({
        'validation_scores': ml_engine.validation_scores,
        'feature_importance': ml_engine.feature_importance,
        'is_trained': ml_engine.is_trained,
        'n_models': len(ml_engine.models),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Homepage enterprise"""
    if not system_initialized:
        initialize_enterprise_system()
    
    return render_template('enterprise.html', sistema_enterprise=True)

if __name__ == '__main__':
    # Inizializza sistema
    initialize_enterprise_system()
    
    logger.info("🌐 Avvio Sistema Enterprise...")
    logger.info("🔗 Server disponibile su: http://localhost:5008")
    
    app.run(
        host='0.0.0.0',
        port=5008,
        debug=False,
        use_reloader=False
    )