#!/usr/bin/env python3
import pandas as pd

# Cerca risultato Roma-Cagliari 
df = pd.read_csv('data/I1_2526.csv')
print(f'📊 Dataset: {len(df)} partite\n')

# Filtra Roma-Cagliari
roma = df[(df['HomeTeam'] == 'Roma') & (df['AwayTeam'] == 'Cagliari')]

if len(roma) > 0:
    row = roma.iloc[0]
    print(f'✅ Roma-Cagliari trovata!')
    print(f'Data: {row["Date"]}')
    print(f'Risultato: {row["FTHG"]}-{row["FTAG"]}')
    
    total = int(row['FTHG']) + int(row['FTAG'])
    result = 'WIN' if total > 2 else 'LOSS'
    print(f'Gol totali: {total} → Over 2.5: {result}')
else:
    print('❌ Non trovata - Ultime partite:')
    print(df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].tail(10))
