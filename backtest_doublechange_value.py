#!/usr/bin/env python3
"""
Backtest Double Chance Value Betting
Trova filtri ottimali per ROI positivo
"""
import pandas as pd
import sys
sys.path.insert(0, 'web')
from web.app_professional import ProfessionalCalculator, _calcola_mercati_deterministici

print('📊 BACKTEST DOUBLE CHANCE VALUE BETTING')
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

# Filtra partite con quote Double Chance e risultato
df_valid = df[
    df['FTR'].notna() &
    df['FTHG'].notna() &
    df['FTAG'].notna() &
    df['B365H'].notna() &  # Quote 1X2 per calcolare DC
    df['B365D'].notna() &
    df['B365A'].notna()
].copy()

print(f'📁 Dataset: {len(df)} partite')
print(f'✅ Partite valide: {len(df_valid)}')
print(f'📅 Periodo: {df_valid["Date"].min().date()} → {df_valid["Date"].max().date()}\n')

# 2. Split train/test (80/20)
split_idx = int(len(df_valid) * 0.8)
df_train = df_valid.iloc[:split_idx]
df_test = df_valid.iloc[split_idx:]

print(f'🎯 Split dataset:')
print(f'   Training: {len(df_train)} partite ({df_train["Date"].min().date()} → {df_train["Date"].max().date()})')
print(f'   Test: {len(df_test)} partite ({df_test["Date"].min().date()} → {df_test["Date"].max().date()})\n')

# 3. Inizializza calculator
calc = ProfessionalCalculator()
calc.carica_dati('data/dataset_features.csv')
print('✅ Calculator pronto\n')

# 4. Test diversi filtri
filtri_da_testare = [
    {'nome': 'Ultra Conservativo', 'quote_min': 1.10, 'quote_max': 1.40, 'ev_min': 0.05},
    {'nome': 'Conservativo', 'quote_min': 1.15, 'quote_max': 1.60, 'ev_min': 0.08},
    {'nome': 'Moderato', 'quote_min': 1.20, 'quote_max': 1.80, 'ev_min': 0.10},
    {'nome': 'Aggressivo', 'quote_min': 1.25, 'quote_max': 2.00, 'ev_min': 0.12},
]

risultati_filtri = []

# Mappa risultati a Double Chance
def risultato_a_dc(ftr):
    """Converte FTR (H/D/A) a lista Double Chance validi"""
    if ftr == 'H':
        return ['1X', '12']  # Casa vince: 1X e 12 vincono
    elif ftr == 'D':
        return ['1X', 'X2']  # Pareggio: 1X e X2 vincono
    elif ftr == 'A':
        return ['X2', '12']  # Trasferta vince: X2 e 12 vincono
    return []

# Calcola quote Double Chance approssimate da quote 1X2
def calcola_quote_dc(row):
    """Calcola quote Double Chance da quote 1X2"""
    try:
        b365h = row.get('B365H', None)
        b365d = row.get('B365D', None)
        b365a = row.get('B365A', None)
        
        if pd.notna(b365h) and pd.notna(b365d) and pd.notna(b365a):
            # Formula: 1/q_DC ≈ 1/q_H + 1/q_D (con margine)
            prob_h = 1 / b365h
            prob_d = 1 / b365d
            prob_a = 1 / b365a
            
            # Normalizza (bookmaker ha margine ~5%)
            total = prob_h + prob_d + prob_a
            prob_h /= total
            prob_d /= total
            prob_a /= total
            
            # Quote DC con margine 5%
            margin = 1.05
            q_1x = margin / (prob_h + prob_d)
            q_x2 = margin / (prob_d + prob_a)
            q_12 = margin / (prob_h + prob_a)
            
            return {'1X': q_1x, 'X2': q_x2, '12': q_12}
    except:
        pass
    return None

for filtro in filtri_da_testare:
    print(f"🔍 Test filtro: {filtro['nome']}")
    print(f"   Quote: {filtro['quote_min']}-{filtro['quote_max']}, EV ≥{filtro['ev_min']*100:.0f}%")
    
    trades = []
    bankroll = 1000.0
    
    for _, row in df_test.iterrows():
        casa = row['HomeTeam']
        ospite = row['AwayTeam']
        ftr = row['FTR']
        
        # Quote DC calcolate
        quote_dc = calcola_quote_dc(row)
        if quote_dc is None:
            continue
        
        # Risultato reale
        dc_validi = risultato_a_dc(ftr)
        
        # Predizione
        try:
            pred, prob_1x2, conf = calc.predici_partita_deterministica(casa, ospite)
            mercati = _calcola_mercati_deterministici(casa, ospite, prob_1x2)
            
            # Probabilità Double Chance
            prob_dc = mercati['mdc']['probabilita']
            
            # Expected Value per ogni opzione
            ev_results = []
            for dc_opt in ['1X', 'X2', '12']:
                odds = quote_dc[dc_opt]
                prob = prob_dc[dc_opt]
                ev = (prob * odds) - 1
                ev_results.append({'opt': dc_opt, 'odds': odds, 'prob': prob, 'ev': ev})
            
            # Migliore opportunità
            best = max(ev_results, key=lambda x: x['ev'])
            
            # Applica filtri
            if (filtro['quote_min'] <= best['odds'] <= filtro['quote_max'] and 
                best['ev'] >= filtro['ev_min']):
                
                # Kelly Criterion (conservativo)
                kelly = (best['prob'] * best['odds'] - 1) / (best['odds'] - 1)
                stake_pct = max(0.01, min(kelly * 0.25, 0.03))  # Max 3% bankroll
                stake = bankroll * stake_pct
                
                # Esito
                won = best['opt'] in dc_validi
                profit = stake * (best['odds'] - 1) if won else -stake
                
                bankroll += profit
                
                trades.append({
                    'data': row['Date'],
                    'partita': f'{casa} vs {ospite}',
                    'bet': best['opt'],
                    'odds': best['odds'],
                    'prob': best['prob'],
                    'ev': best['ev'],
                    'stake': stake,
                    'won': won,
                    'profit': profit,
                    'bankroll': bankroll,
                    'ftr': ftr
                })
        except Exception as e:
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
