#!/usr/bin/env python3
"""
Backtest Over/Under 2.5 Value Betting
Trova filtri ottimali per ROI positivo
"""
import pandas as pd
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('📊 BACKTEST OVER/UNDER 2.5 VALUE BETTING')
print('=' * 80)

# 1. Carica tutti i CSV stagionali con quote
csv_files = [
    'data/I1_2021.csv',
    'data/I1_2122.csv', 
    'data/I1_2223.csv',
    'data/I1_2324.csv',
    'data/I1_2425.csv',
    'data/I1_2526.csv'
]

dfs = []
for csv_file in csv_files:
    try:
        df_temp = pd.read_csv(csv_file)
        df_temp['Date'] = pd.to_datetime(df_temp['Date'], format='%d/%m/%Y', errors='coerce')
        dfs.append(df_temp)
        print(f'✅ Caricato: {csv_file.split("/")[-1]} ({len(df_temp)} partite)')
    except Exception as e:
        print(f'⚠️  Errore caricamento {csv_file}: {e}')

df = pd.concat(dfs, ignore_index=True)
df = df.sort_values('Date')

# Filtra partite con quote Over/Under e risultato
df_valid = df[
    df['FTR'].notna() &
    df['FTHG'].notna() &
    df['FTAG'].notna() &
    df['Avg>2.5'].notna() &  # Quote Over 2.5 (media bookmaker)
    df['Avg<2.5'].notna()    # Quote Under 2.5 (media bookmaker)
].copy()

print(f'📁 Dataset: {len(df)} partite')
print(f'✅ Partite con quote O/U: {len(df_valid)}')
print(f'📅 Periodo: {df_valid["Date"].min().date()} → {df_valid["Date"].max().date()}\n')

# 2. Split train/test (80/20)
split_idx = int(len(df_valid) * 0.8)
df_train = df_valid.iloc[:split_idx]
df_test = df_valid.iloc[split_idx:]

print(f'\n🎯 Split dataset:')
print(f'   Training: {len(df_train)} partite ({df_train["Date"].min().date()} → {df_train["Date"].max().date()})')
print(f'   Test: {len(df_test)} partite ({df_test["Date"].min().date()} → {df_test["Date"].max().date()})\n')

# 3. Inizializza calculator
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')
print('✅ Calculator pronto\n')

# 4. Test diversi filtri
filtri_da_testare = [
    {'nome': 'Conservativo', 'quote_min': 1.80, 'quote_max': 2.20, 'ev_min': 0.20},
    {'nome': 'Moderato', 'quote_min': 1.70, 'quote_max': 2.50, 'ev_min': 0.15},
    {'nome': 'Aggressivo', 'quote_min': 1.60, 'quote_max': 2.80, 'ev_min': 0.10},
    {'nome': 'Range Alto', 'quote_min': 2.00, 'quote_max': 2.50, 'ev_min': 0.15},
]

risultati_filtri = []

for filtro in filtri_da_testare:
    print(f"🔍 Test filtro: {filtro['nome']}")
    print(f"   Quote: {filtro['quote_min']}-{filtro['quote_max']}, EV ≥{filtro['ev_min']*100:.0f}%")
    
    trades = []
    bankroll = 1000.0
    
    for _, row in df_test.iterrows():
        casa = row['HomeTeam']
        ospite = row['AwayTeam']
        
        # Quote reali (media bookmaker)
        odds_over = row['Avg>2.5']
        odds_under = row['Avg<2.5']
        
        # Risultato reale
        gol_tot = row['FTHG'] + row['FTAG']
        risultato_over = gol_tot > 2.5
        
        # Predizione
        try:
            pred, prob_1x2, conf = calc.predici_partita_deterministica(casa, ospite)
            mercati = _calcola_mercati_deterministici(casa, ospite, prob_1x2)
            
            prob_over = mercati['mou25']['probabilita']['over']
            prob_under = mercati['mou25']['probabilita']['under']
            
            # Expected Value
            ev_over = (prob_over * odds_over) - 1
            ev_under = (prob_under * odds_under) - 1
            
            # Filtro migliore opportunità
            best_ev = max(ev_over, ev_under)
            best_bet = 'over' if ev_over > ev_under else 'under'
            best_odds = odds_over if best_bet == 'over' else odds_under
            best_prob = prob_over if best_bet == 'over' else prob_under
            
            # Applica filtri
            if (filtro['quote_min'] <= best_odds <= filtro['quote_max'] and 
                best_ev >= filtro['ev_min']):
                
                # Kelly Criterion (conservativo)
                kelly = (best_prob * best_odds - 1) / (best_odds - 1)
                stake_pct = max(0.01, min(kelly * 0.25, 0.02))  # Max 2% bankroll
                stake = bankroll * stake_pct
                
                # Esito
                won = (best_bet == 'over' and risultato_over) or (best_bet == 'under' and not risultato_over)
                profit = stake * (best_odds - 1) if won else -stake
                
                bankroll += profit
                
                trades.append({
                    'data': row['Date'],
                    'partita': f'{casa} vs {ospite}',
                    'bet': best_bet,
                    'odds': best_odds,
                    'prob': best_prob,
                    'ev': best_ev,
                    'stake': stake,
                    'won': won,
                    'profit': profit,
                    'bankroll': bankroll
                })
        except:
            continue
    
    if len(trades) > 0:
        df_trades = pd.DataFrame(trades)
        roi = (bankroll - 1000) / 1000 * 100
        win_rate = df_trades['won'].sum() / len(df_trades) * 100
        profit_totale = bankroll - 1000
        ev_medio = df_trades['ev'].mean() * 100
        
        # Calcola max drawdown
        df_trades['peak'] = df_trades['bankroll'].cummax()
        df_trades['drawdown'] = (df_trades['bankroll'] - df_trades['peak']) / df_trades['peak'] * 100
        max_dd = df_trades['drawdown'].min()
        
        risultati_filtri.append({
            'filtro': filtro['nome'],
            'quote_range': f"{filtro['quote_min']}-{filtro['quote_max']}",
            'ev_min': filtro['ev_min'],
            'trades': len(df_trades),
            'win_rate': win_rate,
            'roi': roi,
            'profit': profit_totale,
            'ev_medio': ev_medio,
            'max_dd': max_dd
        })
        
        print(f"   ✅ Trade: {len(df_trades)}, WR: {win_rate:.1f}%, ROI: {roi:+.2f}%")
        print(f"   💰 Profit: €{profit_totale:+.2f}, Max DD: {max_dd:.1f}%\n")
    else:
        print(f"   ❌ Nessun trade trovato\n")

# 5. Risultati finali
print('=' * 80)
print('📈 RISULTATI COMPARATIVI')
print('=' * 80)

if risultati_filtri:
    df_risultati = pd.DataFrame(risultati_filtri)
    df_risultati = df_risultati.sort_values('roi', ascending=False)
    
    print(df_risultati.to_string(index=False))
    
    print('\n' + '=' * 80)
    print('🏆 FILTRO MIGLIORE')
    print('=' * 80)
    
    best = df_risultati.iloc[0]
    print(f"\nFiltro: {best['filtro']}")
    print(f"Quote range: {best['quote_range']}")
    print(f"EV minimo: {best['ev_min']*100:.0f}%")
    print(f"\n✅ Trade: {best['trades']}")
    print(f"✅ Win Rate: {best['win_rate']:.1f}%")
    print(f"✅ ROI: {best['roi']:+.2f}%")
    print(f"✅ Profit: €{best['profit']:+.2f}")
    print(f"✅ EV medio: {best['ev_medio']:.1f}%")
    print(f"⚠️  Max Drawdown: {best['max_dd']:.1f}%")
    
    if best['roi'] > 3:
        print('\n🎉 FILTRO VALIDATO - ROI >3%!')
    else:
        print('\n⚠️  ROI insufficiente - richiede ottimizzazione')
else:
    print('❌ Nessun risultato valido')

print('\n' + '=' * 80)
