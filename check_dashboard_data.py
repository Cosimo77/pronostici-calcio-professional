#!/usr/bin/env python3
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('tracking_predictions_live.csv')

# Filtra solo predizioni con risultato
df_risultati = df[df['Corretto'].notna()]
print(f'📊 Predizioni con risultato: {len(df_risultati)}')

# Ultimi 30 giorni
today = datetime(2026, 3, 28)
thirty_days_ago = today - timedelta(days=30)
df['Data_dt'] = pd.to_datetime(df['Data'])
df_30d = df[(df['Data_dt'] >= thirty_days_ago) & (df['Corretto'].notna())]

print(f'\n📅 Ultimi 30 giorni (dal {thirty_days_ago.date()}): {len(df_30d)} predizioni')
print(f'   Range effettivo: {df_30d["Data"].min()} → {df_30d["Data"].max()}')

# Accuracy
corrette_30d = df_30d['Corretto'].sum()
accuracy_30d = (corrette_30d / len(df_30d) * 100) if len(df_30d) > 0 else 0
print(f'   ✅ Corrette: {int(corrette_30d)}/{len(df_30d)} = {accuracy_30d:.2f}%')

# Profit
profit_30d = df_30d['Profit'].sum()
print(f'   💰 Profit: {profit_30d:+.2f} unità')

# Lifetime (tutto)
corrette_lifetime = df_risultati['Corretto'].sum()
accuracy_lifetime = (corrette_lifetime / len(df_risultati) * 100)
profit_lifetime = df_risultati['Profit'].sum()
print(f'\n📈 Lifetime (tutto il periodo): {int(corrette_lifetime)}/{len(df_risultati)} = {accuracy_lifetime:.2f}%')
print(f'   💰 Profit lifetime: {profit_lifetime:+.2f} unità')

# Breakdown per mercato (ultimi 30gg)
print(f'\n🎯 Breakdown per mercato (ultimi 30 giorni):')
for mercato in df_30d['Mercato'].unique():
    df_merc = df_30d[df_30d['Mercato'] == mercato]
    corrette_merc = df_merc['Corretto'].sum()
    totali_merc = len(df_merc)
    acc_merc = (corrette_merc / totali_merc * 100) if totali_merc > 0 else 0
    print(f'   {mercato}: {acc_merc:.1f}% ({int(corrette_merc)}/{totali_merc})')
