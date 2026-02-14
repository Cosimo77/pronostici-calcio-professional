#!/usr/bin/env python3
"""
GENERA TRACKING FASE 2 - Crea CSV per monitoraggio performance reale
Estrae opportunità validate dal sistema e le salva in formato tracciabile
"""
import requests
import csv
import os
from datetime import datetime
import sys

def genera_tracking_fase2():
    """Estrae opportunità FASE 2 e crea CSV di tracking"""
    
    # URL endpoint (locale o produzione)
    if len(sys.argv) > 1 and sys.argv[1] == '--local':
        url = 'http://localhost:5008/api/upcoming_matches'
        print("📍 Modalità LOCALE (porta 5008)")
    else:
        url = 'https://pronostici-calcio-pro.onrender.com/api/upcoming_matches'
        print("📍 Modalità PRODUZIONE")
    
    print(f"📡 Connessione a {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Errore connessione API: {e}")
        return False
    
    matches = data.get('matches', [])
    print(f"✅ Ricevute {len(matches)} partite\n")
    
    # File di output
    output_file = 'tracking_fase2_febbraio2026.csv'
    
    # Raccogli tutte le opportunità
    opportunita = []
    for match in matches:
        vb = match.get('value_betting', {})
        
        if not vb.get('fase2_validated'):
            continue
        
        home = match.get('home_team_display', match.get('home_team'))
        away = match.get('away_team_display', match.get('away_team'))
        commence_time = match.get('commence_time', '')
        data_match = commence_time[:10] if commence_time else 'N/A'
        
        for opp in vb.get('fase2_opportunities', []):
            opportunita.append({
                'Data': data_match,
                'Casa': home,
                'Ospite': away,
                'Mercato': opp.get('market', 'N/A'),
                'Esito': opp.get('outcome', 'N/A'),
                'Quota': round(opp.get('odds', 0), 2),
                'EV_%': round(opp.get('ev', 0), 1),
                'Prob_Modello_%': round(opp.get('prob_model', 0), 1),  # API già ritorna %
                'Strategia': opp.get('strategy', 'N/A'),
                'ROI_Backtest': opp.get('roi_backtest', 'N/A'),
                'Stake_Suggerito': round(500 * 0.02, 2),  # 2% bankroll
                'Giocata': 'NO',  # Default: non giocata (cambia in SI se scommetti)
                'Risultato': 'PENDING',
                'Profit_Loss': 0.0,
                'Bankroll': 500.0,
                'Note': f"Auto-generato {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            })
    
    if not opportunita:
        print("⚠️  Nessuna opportunità FASE 2 trovata")
        return False
    
    # Ordina per data e poi per EV decrescente
    opportunita.sort(key=lambda x: (x['Data'], -x['EV_%']))
    
    # Scrivi CSV
    fieldnames = [
        'Data', 'Casa', 'Ospite', 'Mercato', 'Esito', 'Quota',
        'EV_%', 'Prob_Modello_%', 'Strategia', 'ROI_Backtest',
        'Stake_Suggerito', 'Giocata', 'Risultato', 'Profit_Loss', 'Bankroll', 'Note'
    ]
    
    # Mantieni trade precedenti già giocati (Giocata=SI)
    trade_storici = []
    bankroll_corrente = 500.0  # Default iniziale
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Giocata') == 'SI':
                    trade_storici.append(row)
                    # Aggiorna bankroll dall'ultimo trade giocato
                    try:
                        bankroll_corrente = float(row.get('Bankroll', bankroll_corrente))
                    except (ValueError, TypeError):
                        pass
    
    # Aggiorna bankroll delle nuove opportunità
    for opp in opportunita:
        opp['Bankroll'] = bankroll_corrente
    
    # Combina: prima trade storici, poi nuove opportunità
    tutti_trade = trade_storici + opportunita
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tutti_trade)
    
    print(f"✅ Creato {output_file}")
    print(f"📊 Opportunità salvate: {len(opportunita)}\n")
    
    # Stampa riepilogo per strategia
    from collections import Counter
    strategie = Counter(opp['Strategia'] for opp in opportunita)
    
    print("📈 Riepilogo per Strategia:")
    print("=" * 60)
    for strategia, count in strategie.most_common():
        roi = opportunita[0].get('ROI_Backtest', 'N/A')  # Prendi primo ROI
        print(f"  • {strategia}: {count} opportunità (ROI backtest: {roi})")
    
    print("\n" + "=" * 60)
    print("📋 Prime 5 opportunità per EV:")
    print("=" * 60)
    for i, opp in enumerate(opportunita[:5], 1):
        print(f"\n{i}. {opp['Casa']} vs {opp['Ospite']}")
        print(f"   Mercato: {opp['Mercato']} - {opp['Esito']}")
        print(f"   Quota: {opp['Quota']} | EV: +{opp['EV_%']}% | Stake: €{opp['Stake_Suggerito']}")
        print(f"   Strategia: {opp['Strategia']} (ROI backtest: {opp['ROI_Backtest']})")
    
    print("\n" + "=" * 60)
    print("💡 PROSSIMI STEP:")
    print("=" * 60)
    print("1. Rivedi il file tracking_fase2_febbraio2026.csv")
    print("2. Quando le partite finiscono, aggiorna colonna 'Risultato':")
    print("   - WIN se scommessa vinta")
    print("   - LOSS se scommessa persa")
    print("   - VOID se partita annullata")
    print("3. Esegui 'python aggiorna_tracking_fase2.py' per calcolare P&L")
    print("4. Visita http://localhost:5000/tracking per dashboard visuale")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = genera_tracking_fase2()
    sys.exit(0 if success else 1)
