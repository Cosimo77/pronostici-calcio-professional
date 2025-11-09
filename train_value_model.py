#!/usr/bin/env python3
"""
Modello VALUE-ORIENTED per battere i bookmaker
Train con obiettivo ROI, non solo accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def calculate_expected_value(prob_model, odds):
    """
    Calcola Expected Value della scommessa
    
    EV = (probabilità vittoria * guadagno) - (probabilità perdita * puntata)
    EV = (prob * (odds - 1)) - ((1 - prob) * 1)
    EV = prob * odds - 1
    
    Se EV > 0 → value bet (punta!)
    Se EV < 0 → no value (skip)
    """
    return prob_model * odds - 1

def create_value_weights(y, odds_h, odds_d, odds_a):
    """
    Crea pesi campioni basati su potential ROI
    Sample con alto ROI potenziale → peso maggiore nel training
    """
    weights = np.ones(len(y))
    
    for i in range(len(y)):
        outcome = y.iloc[i]
        
        if outcome == 0:  # Casa vinta
            odds = odds_h.iloc[i]
        elif outcome == 1:  # Pareggio
            odds = odds_d.iloc[i]
        else:  # Trasferta vinta
            odds = odds_a.iloc[i]
        
        # Peso = potenziale guadagno
        # Quote alte = sorprese = impara meglio questi casi
        weight = max(odds - 1, 0.5)  # Min 0.5x, max infinito
        weights[i] = weight
    
    # Normalizza
    weights = weights / weights.mean()
    return weights

print("💰 TRAINING MODELLO VALUE-ORIENTED ANTI-BOOKMAKER")
print("=" * 70)

# 1. Carica dataset
print("\n📂 Caricamento dataset...")
df = pd.read_csv('data/dataset_features.csv')
y = df['FTR'].map({'H': 0, 'D': 1, 'A': 2})

# Feature (top 20 per performance)
feature_importance = pd.read_csv('cache/feature_importance.csv')
top_features = feature_importance.head(20)['feature'].tolist()

print(f"   Partite: {len(df)}")
print(f"   Feature selezionate: {len(top_features)} (top 20)")

X = df[top_features].fillna(df[top_features].median())

# Quote per calcolo EV
odds_h = df['AvgH']
odds_d = df['AvgD']
odds_a = df['AvgA']

# 2. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Split odds corrispondenti
odds_h_train, odds_h_test = train_test_split(odds_h, test_size=0.2, random_state=42, stratify=y)
odds_d_train, odds_d_test = train_test_split(odds_d, test_size=0.2, random_state=42, stratify=y)
odds_a_train, odds_a_test = train_test_split(odds_a, test_size=0.2, random_state=42, stratify=y)

print(f"\n📊 Split: {len(X_train)} train, {len(X_test)} test")

# 3. Crea pesi VALUE-ORIENTED
print("\n⚖️  Creazione pesi value-oriented...")
sample_weights = create_value_weights(y_train, odds_h_train, odds_d_train, odds_a_train)
print(f"   Peso medio: {sample_weights.mean():.2f}")
print(f"   Peso min: {sample_weights.min():.2f}, max: {sample_weights.max():.2f}")

# 4. Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Training modelli VALUE-ORIENTED
print("\n" + "="*70)
print("🎯 TRAINING MODELLI VALUE-ORIENTED")
print("="*70)

# Gradient Boosting (migliore con quote)
print("\n🤖 GradientBoosting VALUE")
gb_value = GradientBoostingClassifier(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.05,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42
)

# Train con sample weights (enfatizza value bets)
gb_value.fit(X_train_scaled, y_train, sample_weight=sample_weights)

# Predict con probabilità
y_pred = gb_value.predict(X_test_scaled)
y_pred_proba = gb_value.predict_proba(X_test_scaled)

# Accuracy normale
acc = accuracy_score(y_test, y_pred)
print(f"   Accuracy test: {acc*100:.1f}%")

# 6. Calcola ROI con VALUE BETTING
print("\n" + "="*70)
print("💰 STRATEGIA VALUE BETTING")
print("="*70)

results = []

for i in range(len(y_test)):
    true_outcome = y_test.iloc[i]
    pred_outcome = y_pred[i]
    probs = y_pred_proba[i]
    
    odds = [odds_h_test.iloc[i], odds_d_test.iloc[i], odds_a_test.iloc[i]]
    
    # Calcola EV per ogni esito
    ev_h = calculate_expected_value(probs[0], odds[0])
    ev_d = calculate_expected_value(probs[1], odds[1])
    ev_a = calculate_expected_value(probs[2], odds[2])
    
    evs = [ev_h, ev_d, ev_a]
    max_ev = max(evs)
    max_ev_outcome = np.argmax(evs)
    
    # Confidenza
    confidence = probs[max_ev_outcome]
    
    results.append({
        'true': true_outcome,
        'pred': pred_outcome,
        'best_ev_outcome': max_ev_outcome,
        'best_ev': max_ev,
        'confidence': confidence,
        'odds_h': odds[0],
        'odds_d': odds[1],
        'odds_a': odds[2],
        'prob_h': probs[0],
        'prob_d': probs[1],
        'prob_a': probs[2]
    })

results_df = pd.DataFrame(results)

# Strategia 1: Punta SEMPRE (baseline)
print("\n📊 STRATEGIA 1: Punta sempre sul modello")
correct_always = (results_df['pred'] == results_df['true']).sum()
acc_always = correct_always / len(results_df)

roi_always = []
for _, row in results_df.iterrows():
    pred = int(row['pred'])
    true = int(row['true'])
    odds = [row['odds_h'], row['odds_d'], row['odds_a']]
    
    if pred == true:
        roi_always.append(odds[pred] - 1)
    else:
        roi_always.append(-1)

roi_always_mean = np.mean(roi_always)
roi_always_cum = np.sum(roi_always)

print(f"   Accuracy: {acc_always*100:.1f}%")
print(f"   ROI medio: {roi_always_mean*100:+.2f}%")
print(f"   Profit: {roi_always_cum:+.2f}€ (su {len(results_df)} partite)")

# Strategia 2: Punta SOLO su value bets (EV > 0)
print("\n📊 STRATEGIA 2: Punta SOLO se EV > 0 (VALUE BETTING)")
value_bets = results_df[results_df['best_ev'] > 0]
print(f"   Value bets trovati: {len(value_bets)}/{len(results_df)} ({len(value_bets)/len(results_df)*100:.1f}%)")

if len(value_bets) > 0:
    roi_value = []
    for _, row in value_bets.iterrows():
        best_ev_outcome = int(row['best_ev_outcome'])
        true = int(row['true'])
        odds = [row['odds_h'], row['odds_d'], row['odds_a']]
        
        if best_ev_outcome == true:
            roi_value.append(odds[best_ev_outcome] - 1)
        else:
            roi_value.append(-1)
    
    correct_value = sum(1 for r in roi_value if r > 0)
    acc_value = correct_value / len(value_bets)
    roi_value_mean = np.mean(roi_value)
    roi_value_cum = np.sum(roi_value)
    
    print(f"   Accuracy su value bets: {acc_value*100:.1f}%")
    print(f"   ROI medio: {roi_value_mean*100:+.2f}%")
    print(f"   Profit: {roi_value_cum:+.2f}€ (su {len(value_bets)} scommesse)")

# Strategia 3: High confidence + value (EV > 5% AND confidence > 60%)
print("\n📊 STRATEGIA 3: HIGH CONFIDENCE VALUE (EV>5% + Conf>60%)")
high_value = results_df[(results_df['best_ev'] > 0.05) & (results_df['confidence'] > 0.6)]
print(f"   Scommesse selezionate: {len(high_value)}/{len(results_df)} ({len(high_value)/len(results_df)*100:.1f}%)")

if len(high_value) > 0:
    roi_high = []
    for _, row in high_value.iterrows():
        best_ev_outcome = int(row['best_ev_outcome'])
        true = int(row['true'])
        odds = [row['odds_h'], row['odds_d'], row['odds_a']]
        
        if best_ev_outcome == true:
            roi_high.append(odds[best_ev_outcome] - 1)
        else:
            roi_high.append(-1)
    
    correct_high = sum(1 for r in roi_high if r > 0)
    acc_high = correct_high / len(high_value)
    roi_high_mean = np.mean(roi_high)
    roi_high_cum = np.sum(roi_high)
    
    print(f"   Accuracy: {acc_high*100:.1f}%")
    print(f"   ROI medio: {roi_high_mean*100:+.2f}%")
    print(f"   Profit: {roi_high_cum:+.2f}€ (su {len(high_value)} scommesse)")

# 7. Confronto con bookmaker
print("\n" + "="*70)
print("📊 CONFRONTO VS BOOKMAKER")
print("="*70)

# Bookmaker predictions (seguire favorito)
book_preds = []
for _, row in results_df.iterrows():
    probs = [row['prob_h'], row['prob_d'], row['prob_a']]
    book_preds.append(np.argmax(probs))

book_correct = sum(1 for i in range(len(book_preds)) if book_preds[i] == results_df.iloc[i]['true'])
book_acc = book_correct / len(results_df)

print(f"   Bookmaker accuracy: {book_acc*100:.1f}%")
print(f"   Nostro modello accuracy: {acc_always*100:.1f}%")
print(f"   Differenza: {(acc_always - book_acc)*100:+.1f}%")

# 8. Salva modello
print("\n" + "="*70)
print("💾 SALVATAGGIO MODELLO VALUE-ORIENTED")
print("="*70)

backup_dir = f'models/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}_value'
import os
os.makedirs(backup_dir, exist_ok=True)

with open('models/value_betting_model.pkl', 'wb') as f:
    pickle.dump(gb_value, f)
print("   ✅ value_betting_model.pkl")

with open('models/value_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("   ✅ value_scaler.pkl")

metadata = {
    'model_type': 'value_oriented_gradient_boosting',
    'training_date': datetime.now().isoformat(),
    'feature_columns': top_features,
    'n_features': len(top_features),
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'accuracy': acc_always,
    'roi_always': roi_always_mean,
    'roi_value_betting': roi_value_mean if len(value_bets) > 0 else 0,
    'roi_high_confidence': roi_high_mean if len(high_value) > 0 else 0,
    'value_bets_pct': len(value_bets) / len(results_df) if len(results_df) > 0 else 0,
    'strategy': 'value_betting_ev_threshold'
}

with open('models/value_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)
print("   ✅ value_metadata.pkl")

print("\n" + "="*70)
print("✅ MODELLO VALUE-ORIENTED COMPLETATO!")
print("="*70)
print(f"\n🎯 MIGLIOR STRATEGIA: {'STRATEGIA 3' if len(high_value) > 0 and roi_high_mean > 0 else 'STRATEGIA 2' if len(value_bets) > 0 and roi_value_mean > 0 else 'STRATEGIA 1'}")
if len(high_value) > 0 and roi_high_mean > 0:
    print(f"   • Punta SOLO se EV>5% + Confidenza>60%")
    print(f"   • {len(high_value)} scommesse su {len(results_df)} totali")
    print(f"   • ROI atteso: {roi_high_mean*100:+.2f}%")
    print(f"   • Profit atteso: {roi_high_cum:+.2f}€")

print("="*70)
