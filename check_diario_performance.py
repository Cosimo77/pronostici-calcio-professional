import sys, json, requests

response = requests.get('https://pronostici-calcio-pro.onrender.com/api/diario/all')
data = response.json()

profit = sum(b['profit'] for b in data if b['risultato'] in ['WIN', 'LOSS'])
wins = sum(1 for b in data if b['risultato']=='WIN')
losses = sum(1 for b in data if b['risultato']=='LOSS')
total = wins + losses
wr = (wins/total*100) if total > 0 else 0
stake_total = sum(float(b['stake']) for b in data if b['risultato'] in ['WIN', 'LOSS'] and b['stake'] not in ['MONITOR', ''])
roi = (profit/stake_total*100) if stake_total > 0 else 0

print(f'📊 Performance Diario Betting:')
print(f'   Win Rate: {wr:.1f}% ({wins}W-{losses}L)')
print(f'   Profit totale: {profit:+.2f}€')
print(f'   Stake investito: {stake_total:.2f}€')
print(f'   ROI: {roi:+.1f}%')
print(f'\n🏆 Breakdown per partita:')
for b in data:
    if b['risultato'] != 'PENDING':
        simbolo = '✅' if b['risultato'] == 'WIN' else '❌'
        print(f"   {simbolo} {b['partita']}: {b['mercato']} @ {b['quota_sisal']} → {b['risultato']} ({b['profit']:+.2f}€)")
