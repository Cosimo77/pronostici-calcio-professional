#!/usr/bin/env python3
"""
TEST COMPLETO END-TO-END SISTEMA BETTING
Verifica TUTTO prima di dare OK per trading reale
"""

import sys
import os
import requests
import json
import pandas as pd
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

class TestCompletoBetting:
    """Test rigorosi end-to-end sistema betting"""
    
    def __init__(self):
        self.base_url = 'http://localhost:5008'
        self.errors = []
        self.warnings = []
        
    def log_error(self, test_name, msg):
        """Registra errore critico"""
        self.errors.append(f"❌ {test_name}: {msg}")
        print(f"❌ {test_name}: {msg}")
        
    def log_warning(self, test_name, msg):
        """Registra warning non critico"""
        self.warnings.append(f"⚠️  {test_name}: {msg}")
        print(f"⚠️  {test_name}: {msg}")
        
    def log_success(self, test_name, msg):
        """Registra successo"""
        print(f"✅ {test_name}: {msg}")
    
    # ============================================
    # TEST 1: QUOTE REALI VS INVENTATE
    # ============================================
    def test_quote_reali_non_inventate(self):
        """CRITICO: Verifica che TUTTE le opportunità usino quote REALI da API"""
        print("\n" + "="*70)
        print("TEST 1: QUOTE REALI VS INVENTATE (CRITICO)")
        print("="*70)
        
        try:
            response = requests.get(f'{self.base_url}/api/upcoming_matches', timeout=30)
            if response.status_code != 200:
                self.log_error("Quote Reali", f"API failed: {response.status_code}")
                return False
                
            data = response.json()
            matches = data.get('matches', [])
            
            if len(matches) == 0:
                self.log_warning("Quote Reali", "Nessuna partita disponibile per testare")
                return True
            
            # Verifica OGNI partita
            for match in matches:
                home = match.get('home_team', '?')
                away = match.get('away_team', '?')
                
                # 1. Verifica che odds_real sia popolato
                odds_real = match.get('odds_real', {})
                if not odds_real or odds_real.get('source') != 'The Odds API (REAL)':
                    self.log_error("Quote Reali", 
                        f"{home} vs {away}: odds_real mancante o non da The Odds API")
                    continue
                
                # 2. Verifica che le quote siano numeriche e realistiche
                odds_home = odds_real.get('home', 0)
                odds_draw = odds_real.get('draw', 0)
                odds_away = odds_real.get('away', 0)
                
                if odds_home < 1.0 or odds_home > 100:
                    self.log_error("Quote Reali", 
                        f"{home} vs {away}: odds_home {odds_home} fuori range")
                if odds_draw < 1.0 or odds_draw > 100:
                    self.log_error("Quote Reali", 
                        f"{home} vs {away}: odds_draw {odds_draw} fuori range")
                if odds_away < 1.0 or odds_away > 100:
                    self.log_error("Quote Reali", 
                        f"{home} vs {away}: odds_away {odds_away} fuori range")
                
                # 3. CRITICO: Verifica opportunità value betting
                value_betting = match.get('value_betting', {})
                fase2_opps = value_betting.get('fase2_opportunities', [])
                
                for opp in fase2_opps:
                    mercato = opp.get('mercato', '')
                    esito = opp.get('esito', '')
                    quota = opp.get('quota', 0)
                    ev = opp.get('ev', 0)
                    
                    # VERIFICA CRITICA: Mercato deve essere supportato da API
                    mercati_reali_api = ['1X2', 'OU25']  # The Odds API fornisce solo questi
                    
                    if mercato not in mercati_reali_api:
                        self.log_error("Quote Reali", 
                            f"{home} vs {away}: Mercato '{mercato}' NON supportato da API! "
                            f"Quota {quota:.2f} è INVENTATA (EV {ev:+.1f}%)")
                    
                    # VERIFICA: EV realistici (nessun +300% impossibile)
                    if ev > 100:
                        self.log_error("Quote Reali", 
                            f"{home} vs {away}: EV {ev:+.1f}% IRREALISTICO per {mercato} {esito} @ {quota:.2f}")
                    
                    # VERIFICA: Quote coerenti con mercato
                    if mercato == '1X2':
                        if esito == 'Casa' and abs(quota - odds_home) > 0.1:
                            self.log_error("Quote Reali", 
                                f"{home} vs {away}: Quota Casa opportunità {quota:.2f} != API {odds_home:.2f}")
                        elif esito == 'Pareggio' and abs(quota - odds_draw) > 0.1:
                            self.log_error("Quote Reali", 
                                f"{home} vs {away}: Quota Pareggio opportunità {quota:.2f} != API {odds_draw:.2f}")
                        elif esito == 'Trasferta' and abs(quota - odds_away) > 0.1:
                            self.log_error("Quote Reali", 
                                f"{home} vs {away}: Quota Trasferta opportunità {quota:.2f} != API {odds_away:.2f}")
            
            if len(self.errors) == 0:
                self.log_success("Quote Reali", 
                    f"{len(matches)} partite verificate - TUTTE quote REALI da API")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_error("Quote Reali", f"Exception: {e}")
            return False
    
    # ============================================
    # TEST 2: COERENZA MATEMATICA EV
    # ============================================
    def test_coerenza_matematica_ev(self):
        """Verifica che calcoli EV siano matematicamente corretti"""
        print("\n" + "="*70)
        print("TEST 2: COERENZA MATEMATICA EV")
        print("="*70)
        
        try:
            response = requests.get(f'{self.base_url}/api/upcoming_matches', timeout=30)
            data = response.json()
            matches = data.get('matches', [])
            
            for match in matches:
                home = match.get('home_team', '?')
                away = match.get('away_team', '?')
                
                if not match.get('has_prediction'):
                    continue
                
                # Prendi probabilità modello
                prob_ensemble = match.get('markets', {}).get('probabilita_ensemble', {})
                prob_h = prob_ensemble.get('H', 0)
                prob_d = prob_ensemble.get('D', 0)
                prob_a = prob_ensemble.get('A', 0)
                
                # Prendi quote reali
                odds_real = match.get('odds_real', {})
                odds_h = odds_real.get('home', 0)
                odds_d = odds_real.get('draw', 0)
                odds_a = odds_real.get('away', 0)
                
                # Ricalcola EV manualmente
                if odds_h > 0:
                    ev_h_calc = (prob_h * odds_h - 1) * 100
                    vb = match.get('value_betting', {})
                    ev_h_sistema = vb.get('expected_values', {}).get('Casa', 0) * 100
                    
                    if abs(ev_h_calc - ev_h_sistema) > 1.0:  # tolleranza 1%
                        self.log_error("EV Math", 
                            f"{home} vs {away}: EV Casa calcolato {ev_h_calc:.1f}% != sistema {ev_h_sistema:.1f}%")
            
            self.log_success("EV Math", "Calcoli EV matematicamente coerenti")
            return True
            
        except Exception as e:
            self.log_error("EV Math", f"Exception: {e}")
            return False
    
    # ============================================
    # TEST 3: FILTRI FASE1/FASE2 APPLICATI
    # ============================================
    def test_filtri_fase_applicati(self):
        """Verifica che solo opportunità validate passino i filtri"""
        print("\n" + "="*70)
        print("TEST 3: FILTRI FASE1/FASE2 APPLICATI CORRETTAMENTE")
        print("="*70)
        
        try:
            response = requests.get(f'{self.base_url}/api/upcoming_matches', timeout=30)
            data = response.json()
            matches = data.get('matches', [])
            
            total_opps = 0
            for match in matches:
                fase2_opps = match.get('value_betting', {}).get('fase2_opportunities', [])
                total_opps += len(fase2_opps)
                
                for opp in fase2_opps:
                    mercato = opp.get('mercato', '')
                    esito = opp.get('esito', '')
                    quota = opp.get('quota', 0)
                    ev = opp.get('ev', 0)
                    
                    # FASE 1: Pareggi 1X2
                    if mercato == '1X2' and esito == 'Pareggio':
                        if quota < 2.8:
                            self.log_error("Filtri FASE1", 
                                f"Pareggio @ {quota:.2f} < 2.8 (sotto threshold)")
                        if quota > 3.5:
                            self.log_error("Filtri FASE1", 
                                f"Pareggio @ {quota:.2f} > 3.5 (sopra threshold)")
                        if ev < 25:
                            self.log_error("Filtri FASE1", 
                                f"Pareggio EV {ev:.1f}% < 25% (sotto threshold)")
                    
                    # FASE 2: Under 2.5 (sweet spot 20-25%)
                    if mercato == 'OU25' and esito == 'Under':
                        if ev < 20 or ev > 25:
                            self.log_error("Filtri FASE2", 
                                f"Under 2.5 EV {ev:.1f}% fuori sweet spot 20-25%")
                    
                    # VERIFICHE GENERALI
                    if ev < 0:
                        self.log_error("Filtri Generali", 
                            f"Opportunità con EV negativo {ev:.1f}% ({mercato} {esito})")
            
            self.log_success("Filtri", 
                f"{total_opps} opportunità validate - filtri applicati correttamente")
            return True
            
        except Exception as e:
            self.log_error("Filtri", f"Exception: {e}")
            return False
    
    # ============================================
    # TEST 4: DATI SERIE A FRESCHI
    # ============================================
    def test_dati_freschi(self):
        """Verifica che dataset Serie A sia aggiornato (<7 giorni)"""
        print("\n" + "="*70)
        print("TEST 4: DATI SERIE A FRESCHI")
        print("="*70)
        
        try:
            df = pd.read_csv('data/I1_2526.csv')
            ultima_data_str = df['Date'].iloc[-1]
            ultima_data = pd.to_datetime(ultima_data_str, format='%d/%m/%Y')
            oggi = datetime.now()
            giorni_diff = (oggi - ultima_data).days
            
            if giorni_diff > 7:
                self.log_error("Dati Freschi", 
                    f"Ultima partita {giorni_diff} giorni fa (> 7 giorni threshold)")
                return False
            else:
                self.log_success("Dati Freschi", 
                    f"{len(df)} partite, ultima {ultima_data_str} ({giorni_diff} giorni)")
                return True
                
        except Exception as e:
            self.log_error("Dati Freschi", f"Exception: {e}")
            return False
    
    # ============================================
    # TEST 5: PROBABILITÀ COERENTI (SOMMA = 1.0)
    # ============================================
    def test_probabilita_coerenti(self):
        """Verifica che probabilità 1X2 sommino sempre a 1.0"""
        print("\n" + "="*70)
        print("TEST 5: PROBABILITÀ COERENTI")
        print("="*70)
        
        try:
            response = requests.get(f'{self.base_url}/api/upcoming_matches', timeout=30)
            data = response.json()
            matches = data.get('matches', [])
            
            for match in matches:
                if not match.get('has_prediction'):
                    continue
                
                home = match.get('home_team', '?')
                away = match.get('away_team', '?')
                
                prob_ensemble = match.get('markets', {}).get('probabilita_ensemble', {})
                prob_h = prob_ensemble.get('H', 0)
                prob_d = prob_ensemble.get('D', 0)
                prob_a = prob_ensemble.get('A', 0)
                
                somma = prob_h + prob_d + prob_a
                
                if abs(somma - 1.0) > 0.001:  # tolleranza 0.1%
                    self.log_error("Probabilità", 
                        f"{home} vs {away}: Somma {somma:.4f} != 1.0 "
                        f"(H:{prob_h:.3f} D:{prob_d:.3f} A:{prob_a:.3f})")
            
            self.log_success("Probabilità", "Tutte le probabilità sommano a 1.0")
            return True
            
        except Exception as e:
            self.log_error("Probabilità", f"Exception: {e}")
            return False
    
    # ============================================
    # RUN ALL TESTS
    # ============================================
    def run_all(self):
        """Esegui tutti i test"""
        print("\n" + "="*70)
        print("🔍 TEST COMPLETO END-TO-END SISTEMA BETTING")
        print("="*70)
        
        tests = [
            ("Quote Reali vs Inventate", self.test_quote_reali_non_inventate),
            ("Coerenza Matematica EV", self.test_coerenza_matematica_ev),
            ("Filtri FASE1/FASE2", self.test_filtri_fase_applicati),
            ("Dati Serie A Freschi", self.test_dati_freschi),
            ("Probabilità Coerenti", self.test_probabilita_coerenti)
        ]
        
        results = []
        for test_name, test_func in tests:
            result = test_func()
            results.append(result)
        
        # Report finale
        print("\n" + "="*70)
        print("📊 REPORT FINALE")
        print("="*70)
        
        print(f"\n✅ Test passati: {sum(results)}/{len(results)}")
        print(f"❌ Test falliti: {len(results) - sum(results)}/{len(results)}")
        print(f"⚠️  Warning: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ ERRORI CRITICI ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNING ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print("\n" + "="*70)
        if all(results) and len(self.errors) == 0:
            print("✅ SISTEMA CERTIFICATO - PRONTO PER TRADING REALE")
            print("="*70)
            return 0
        else:
            print("❌ SISTEMA NON PRONTO - FIX RICHIESTI PRIMA DI TRADING")
            print("="*70)
            return 1


if __name__ == '__main__':
    tester = TestCompletoBetting()
    exit_code = tester.run_all()
    sys.exit(exit_code)
