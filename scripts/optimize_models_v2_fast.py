#!/usr/bin/env python3
"""
FASE 2 - Riaddestramento VELOCE con Dataset V2 (53 features)
GridSearch ridotto: 12-16 combinazioni invece di 48+ per modello
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import lightgbm as lgb
import xgboost as xgb
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    start_time = datetime.now()
    print("=" * 70)
    print("  RIADDESTRAMENTO VELOCE - DATASET V2 (53 FEATURES)")
    print("=" * 70)
    print(f"Inizio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Caricamento dataset V2
    print("[1/5] Caricamento dataset V2...")
    df = pd.read_csv('data/dataset_features_v2.csv')
    print(f"   Partite: {len(df)}")
    print(f"   Features totali: {len(df.columns)}\n")
    
    # 2. Preparazione dati
    print("[2/5] Preparazione dati...")
    
    # CRITICAL: Escludi FTHG/FTAG (gol partita) che causano data leakage!
    exclude_cols = ['FTR', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    X = df[feature_cols]
    y = df['FTR']
    
    nuove_features = [c for c in feature_cols if any(k in c for k in [
        'forma_recente', 'gol_segnati', 'gol_subiti', 'clean_sheets', 
        'giorni_riposo', 'xg_stimato', 'diff_', 'forma_weighted', 'streak'
    ])]
    
    print(f"   Features usate: {len(feature_cols)}")
    print(f"   Nuove features FASE 2: {len(nuove_features)}")
    print(f"   ⚠️  Escluse (data leakage): FTHG, FTAG")
    
    # Split SENZA stratify (come baseline)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Label encoding per XGBoost/LightGBM
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)
    print(f"   Target encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")  # type: ignore[arg-type]
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("   ✓ Scaling applicato\n")
    
    # Baseline FASE 1 per confronto
    baseline_fase1 = {
        'RF': 0.5046,
        'LightGBM': 0.4679,
        'XGBoost': 0.4917,
        'Voting': 0.4789,
        'Media': 0.4881
    }
    baseline_originale = 0.4783
    
    # 3. Random Forest con GridSearch RIDOTTO
    print("[3/5] Random Forest GridSearch (16 combinazioni)...")
    
    rf_param_grid = {
        'n_estimators': [200, 300],  # Ridotto da 4 a 2 valori
        'max_depth': [25, None],  # Ridotto da 4 a 2 valori
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2]
    }
    
    rf_start = datetime.now()
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        rf_param_grid,
        cv=3,  # Ridotto da 5 a 3 fold per velocità
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    
    rf_grid.fit(X_train, y_train)
    rf_best = rf_grid.best_estimator_
    rf_acc = accuracy_score(y_test, rf_best.predict(X_test))
    rf_time = (datetime.now() - rf_start).seconds
    
    print(f"   ✓ Completato in {rf_time}s")
    print(f"   Best params: {rf_grid.best_params_}")
    print(f"   Cross-val score: {rf_grid.best_score_:.4f}")
    print(f"   Test accuracy: {rf_acc:.4f}")
    print(f"   FASE 1: {baseline_fase1['RF']:.4f} → FASE 2: {rf_acc:.4f} ({(rf_acc - baseline_fase1['RF'])*100:+.2f}%)\n")
    
    # 4. LightGBM con GridSearch RIDOTTO
    print("[4/5] LightGBM GridSearch (12 combinazioni)...")
    
    lgb_param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [15, 20],
        'learning_rate': [0.05, 0.1],
        'num_leaves': [31, 50, 70]
    }
    
    lgb_start = datetime.now()
    lgb_grid = GridSearchCV(
        lgb.LGBMClassifier(random_state=42, verbose=-1),  # type: ignore[arg-type]
        lgb_param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=0
    )
    
    lgb_grid.fit(X_train, y_train_encoded)
    lgb_best = lgb_grid.best_estimator_
    lgb_acc = accuracy_score(y_test_encoded, lgb_best.predict(X_test))  # type: ignore[attr-defined]
    lgb_time = (datetime.now() - lgb_start).seconds
    
    print(f"   ✓ Completato in {lgb_time}s")
    print(f"   Best params: {lgb_grid.best_params_}")
    print(f"   Test accuracy: {lgb_acc:.4f}")
    print(f"   FASE 1: {baseline_fase1['LightGBM']:.4f} → FASE 2: {lgb_acc:.4f} ({(lgb_acc - baseline_fase1['LightGBM'])*100:+.2f}%)\n")
    
    # 5. XGBoost con GridSearch RIDOTTO
    print("[5/5] XGBoost GridSearch (12 combinazioni)...")
    
    xgb_param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [7, 10],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 0.9, 1.0]
    }
    
    xgb_start = datetime.now()
    xgb_grid = GridSearchCV(
        xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
        xgb_param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=0
    )
    
    xgb_grid.fit(X_train_scaled, y_train_encoded)
    xgb_best = xgb_grid.best_estimator_
    xgb_acc = accuracy_score(y_test_encoded, xgb_best.predict(X_test_scaled))
    xgb_time = (datetime.now() - xgb_start).seconds
    
    print(f"   ✓ Completato in {xgb_time}s")
    print(f"   Best params: {xgb_grid.best_params_}")
    print(f"   Test accuracy: {xgb_acc:.4f}")
    print(f"   FASE 1: {baseline_fase1['XGBoost']:.4f} → FASE 2: {xgb_acc:.4f} ({(xgb_acc - baseline_fase1['XGBoost'])*100:+.2f}%)\n")
    
    # Voting Ensemble
    print("[ENSEMBLE] Creazione Voting Classifier...")
    voting_clf = VotingClassifier(
        estimators=[
            ('rf', rf_best),
            ('lgb', lgb_best),
            ('xgb', xgb_best)
        ],
        voting='soft'
    )
    
    voting_clf.fit(X_train, y_train_encoded)
    voting_acc = accuracy_score(y_test_encoded, voting_clf.predict(X_test))
    
    print(f"   Voting accuracy: {voting_acc:.4f}")
    print(f"   FASE 1: {baseline_fase1['Voting']:.4f} → FASE 2: {voting_acc:.4f} ({(voting_acc - baseline_fase1['Voting'])*100:+.2f}%)\n")
    
    # Media generale
    media_fase2 = (rf_acc + lgb_acc + xgb_acc + voting_acc) / 4
    
    # RIEPILOGO FINALE
    print("=" * 70)
    print("  RIEPILOGO FASE 2 - RISULTATI FINALI")
    print("=" * 70)
    
    print(f"\n⏱️  TEMPI ESECUZIONE:")
    print(f"   Random Forest: {rf_time}s")
    print(f"   LightGBM: {lgb_time}s")
    print(f"   XGBoost: {xgb_time}s")
    total_time = (datetime.now() - start_time).seconds
    print(f"   TOTALE: {total_time}s (~{total_time//60} min)\n")
    
    print("📊 CONFRONTO BASELINE → FASE 1 → FASE 2:\n")
    print(f"{'Modello':<20} {'Baseline':<12} {'FASE 1':<12} {'FASE 2':<12} {'Δ Tot':<12}")
    print("-" * 70)
    print(f"{'Random Forest':<20} {baseline_originale:<12.4f} {baseline_fase1['RF']:<12.4f} {rf_acc:<12.4f} {rf_acc - baseline_originale:<+12.4f}")
    print(f"{'LightGBM':<20} {baseline_originale:<12.4f} {baseline_fase1['LightGBM']:<12.4f} {lgb_acc:<12.4f} {lgb_acc - baseline_originale:<+12.4f}")
    print(f"{'XGBoost':<20} {baseline_originale:<12.4f} {baseline_fase1['XGBoost']:<12.4f} {xgb_acc:<12.4f} {xgb_acc - baseline_originale:<+12.4f}")
    print(f"{'Voting Ensemble':<20} {baseline_originale:<12.4f} {baseline_fase1['Voting']:<12.4f} {voting_acc:<12.4f} {voting_acc - baseline_originale:<+12.4f}")
    print("-" * 70)
    print(f"{'MEDIA':<20} {baseline_originale:<12.4f} {baseline_fase1['Media']:<12.4f} {media_fase2:<12.4f} {media_fase2 - baseline_originale:<+12.4f}")
    
    gain_fase1 = ((baseline_fase1['Media'] - baseline_originale) / baseline_originale) * 100
    gain_fase2 = ((media_fase2 - baseline_fase1['Media']) / baseline_fase1['Media']) * 100
    gain_totale = ((media_fase2 - baseline_originale) / baseline_originale) * 100
    
    print(f"\n🎯 MIGLIORAMENTI:")
    print(f"   FASE 1 (Hyperparameters):      +{gain_fase1:.2f}%")
    print(f"   FASE 2 (Feature Engineering):  +{gain_fase2:.2f}%")
    print(f"   GAIN CUMULATIVO TOTALE:        +{gain_totale:.2f}%\n")
    
    # Confusion Matrix del modello migliore
    best_model_name, best_model, best_acc = max([
        ('Random Forest', rf_best, rf_acc),
        ('LightGBM', lgb_best, lgb_acc),
        ('XGBoost', xgb_best, xgb_acc),
        ('Voting', voting_clf, voting_acc)
    ], key=lambda x: x[2])
    
    print(f"📈 MODELLO MIGLIORE: {best_model_name} ({best_acc:.4f})\n")
    
    y_pred_encoded = best_model.predict(X_test)  # type: ignore[attr-defined]
    y_test_labels = le.inverse_transform(y_test_encoded)
    y_pred_labels = le.inverse_transform(y_pred_encoded)
    
    print("Classification Report:")
    print(classification_report(y_test_labels, y_pred_labels, 
                                target_names=['Away', 'Draw', 'Home']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=['A', 'D', 'H'])
    print(f"              Predicted")
    print(f"              A    D    H")
    print(f"Actual A    {cm[0][0]:>4} {cm[0][1]:>4} {cm[0][2]:>4}")
    print(f"       D    {cm[1][0]:>4} {cm[1][1]:>4} {cm[1][2]:>4}")
    print(f"       H    {cm[2][0]:>4} {cm[2][1]:>4} {cm[2][2]:>4}\n")
    
    # Decisione deployment
    target_minimo = 0.52  # 52%
    target_ottimo = 0.53  # 53%
    
    print("🎲 RACCOMANDAZIONE DEPLOYMENT:")
    if media_fase2 >= target_ottimo:
        print(f"   ✅ DEPLOY FORTEMENTE RACCOMANDATO")
        print(f"      Accuracy media: {media_fase2:.1%} ≥ Target {target_ottimo:.1%}")
        print(f"      Gain totale: +{gain_totale:.1f}% vs baseline")
        deploy_decision = "DEPLOY_YES"
    elif media_fase2 >= target_minimo:
        print(f"   ⚠️  DEPLOY CON CAUTELA")
        print(f"      Accuracy media: {media_fase2:.1%} ≥ Target minimo {target_minimo:.1%}")
        print(f"      Gain totale: +{gain_totale:.1f}% vs baseline")
        print(f"      Raccomandazione: Deploy + monitoraggio intensivo")
        deploy_decision = "DEPLOY_CAUTIOUS"
    else:
        print(f"   ❌ NON DEPLOYARE")
        print(f"      Accuracy media: {media_fase2:.1%} < Target {target_minimo:.1%}")
        print(f"      Gain totale: +{gain_totale:.1f}% (insufficiente)")
        print(f"\n      Opzioni alternative:")
        print(f"      - SMOTE oversampling per pareggi")
        print(f"      - Stacking meta-learner")
        print(f"      - Calibrazione probabilità")
        print(f"      - Feature selection (RFE)")
        deploy_decision = "NO_DEPLOY"
    
    # Salvataggio modelli
    print("\n[SALVATAGGIO] Salvataggio modelli FASE 2...")
    
    with open('models/enterprise/random_forest_v2.pkl', 'wb') as f:
        pickle.dump(rf_best, f)
    with open('models/enterprise/lightgbm_v2.pkl', 'wb') as f:
        pickle.dump(lgb_best, f)
    with open('models/enterprise/xgboost_v2.pkl', 'wb') as f:
        pickle.dump(xgb_best, f)
    with open('models/enterprise/voting_ensemble_v2.pkl', 'wb') as f:
        pickle.dump(voting_clf, f)
    with open('models/enterprise/scaler_v2.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('models/enterprise/label_encoder_v2.pkl', 'wb') as f:
        pickle.dump(le, f)
    
    print("   ✓ Salvati 6 modelli in models/enterprise/*_v2.pkl")
    
    # Salva riepilogo risultati
    risultati = {
        'timestamp': datetime.now().isoformat(),
        'baseline_originale': baseline_originale,
        'fase1_media': baseline_fase1['Media'],
        'fase2_media': media_fase2,
        'gain_fase1_perc': gain_fase1,
        'gain_fase2_perc': gain_fase2,
        'gain_totale_perc': gain_totale,
        'modelli': {
            'random_forest': {'fase1': baseline_fase1['RF'], 'fase2': rf_acc},
            'lightgbm': {'fase1': baseline_fase1['LightGBM'], 'fase2': lgb_acc},
            'xgboost': {'fase1': baseline_fase1['XGBoost'], 'fase2': xgb_acc},
            'voting': {'fase1': baseline_fase1['Voting'], 'fase2': voting_acc}
        },
        'best_model': best_model_name,
        'best_accuracy': best_acc,
        'deploy_decision': deploy_decision,
        'tempo_esecuzione_sec': total_time
    }
    
    import json
    with open('logs/fase2_risultati.json', 'w') as f:
        json.dump(risultati, f, indent=2)
    
    print("   ✓ Salvato riepilogo: logs/fase2_risultati.json")
    
    print(f"\nCompletato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if deploy_decision in ["DEPLOY_YES", "DEPLOY_CAUTIOUS"]:
        print("\n✅ PROSSIMO STEP: Integrazione e Deploy")
        print("   1. Aggiorna app_professional.py per usare modelli V2")
        print("   2. Test locale predizioni")
        print("   3. Backup modelli attuali")
        print("   4. Deploy su Render")
        print("   Vedi: DEPLOY_CHECKLIST_FASE1.md")
    else:
        print("\n⚠️  PROSSIMO STEP: Ulteriori Miglioramenti Necessari")
        print("   Target non raggiunto. Analizza feature importance e considera:")
        print("   - SMOTE per class balancing")
        print("   - Stacking ensemble")
        print("   - Feature selection")

if __name__ == "__main__":
    main()
