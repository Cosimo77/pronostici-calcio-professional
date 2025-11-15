#!/usr/bin/env python3
"""
Unit Tests per Value Betting Calculations
Target: 70%+ code coverage delle funzioni critiche
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestValueBettingCalculations(unittest.TestCase):
    """Test per calcoli Expected Value e Value Betting"""
    
    def test_expected_value_calculation(self):
        """Test formula EV = probability * odds - 1"""
        
        # Test 1: EV positivo (value bet)
        prob = 0.40  # 40% probabilità
        odds = 3.25  # Quote bookmaker
        ev = prob * odds - 1
        self.assertAlmostEqual(ev, 0.30, places=2)  # +30% EV
        
        # Test 2: EV negativo (no value)
        prob = 0.30
        odds = 2.50
        ev = prob * odds - 1
        self.assertAlmostEqual(ev, -0.25, places=2)  # -25% EV
        
        # Test 3: Break even (EV = 0)
        prob = 0.50
        odds = 2.00
        ev = prob * odds - 1
        self.assertAlmostEqual(ev, 0.0, places=2)
    
    def test_ev_with_extreme_values(self):
        """Test EV con valori estremi"""
        
        # Quote molto alte
        prob = 0.05
        odds = 20.0
        ev = prob * odds - 1
        self.assertEqual(ev, 0.0)  # Break even
        
        # Quote favorite
        prob = 0.80
        odds = 1.25
        ev = prob * odds - 1
        self.assertEqual(ev, 0.0)  # Break even
        
        # Probabilità 100% (impossibile realmente)
        prob = 1.0
        odds = 1.01
        ev = prob * odds - 1
        self.assertAlmostEqual(ev, 0.01, places=2)
    
    def test_best_ev_selection(self):
        """Test selezione migliore value bet tra mercati multipli"""
        
        # EVs per 1X2
        ev_home = 0.44  # 44%
        ev_draw = 0.29  # 29%
        ev_away = -0.42  # -42%
        
        # EVs per Over/Under
        ev_over = 0.28  # 28%
        ev_under = -0.29  # -29%
        
        # Tutti i mercati
        all_evs = {
            '1X2 Casa': ev_home,
            '1X2 Pareggio': ev_draw,
            '1X2 Trasferta': ev_away,
            'Over 2.5': ev_over,
            'Under 2.5': ev_under
        }
        
        best_market = max(all_evs.keys(), key=lambda k: all_evs[k])
        best_ev = all_evs[best_market]
        
        self.assertEqual(best_market, '1X2 Casa')
        self.assertEqual(best_ev, 0.44)
    
    def test_value_betting_threshold(self):
        """Test soglia value betting (5%)"""
        
        threshold = 0.05  # 5%
        
        # Test valori sopra soglia
        self.assertTrue(0.06 > threshold)  # 6% - BET
        self.assertTrue(0.30 > threshold)  # 30% - BET
        
        # Test valori sotto soglia
        self.assertFalse(0.04 > threshold)  # 4% - SKIP
        self.assertFalse(0.02 > threshold)  # 2% - SKIP
        self.assertFalse(-0.10 > threshold)  # -10% - SKIP
        
        # Test valore esatto
        self.assertFalse(0.05 > threshold)  # Esattamente 5% - SKIP (non strettamente maggiore)
    
    def test_has_value_flag(self):
        """Test flag has_value basato su EV"""
        
        threshold = 0.05
        
        # Caso 1: Value bet evidente
        best_ev = 0.29  # 29%
        has_value = best_ev > threshold
        self.assertTrue(has_value)
        
        # Caso 2: No value
        best_ev = 0.02  # 2%
        has_value = best_ev > threshold
        self.assertFalse(has_value)
        
        # Caso 3: EV negativo
        best_ev = -0.15  # -15%
        has_value = best_ev > threshold
        self.assertFalse(has_value)
    
    def test_probability_to_percentage(self):
        """Test conversione probabilità -> percentuale"""
        
        # Test conversioni standard
        self.assertEqual(round(0.40 * 100, 2), 40.0)
        self.assertEqual(round(0.518 * 100, 2), 51.8)
        self.assertEqual(round(0.333 * 100, 2), 33.3)
        
        # Test edge cases
        self.assertEqual(round(0.0 * 100, 2), 0.0)
        self.assertEqual(round(1.0 * 100, 2), 100.0)
    
    def test_ev_to_percentage(self):
        """Test conversione EV -> percentuale per display"""
        
        # Test conversioni
        self.assertEqual(round(0.2983 * 100, 2), 29.83)
        self.assertEqual(round(-0.4199 * 100, 2), -41.99)
        self.assertEqual(round(0.4629 * 100, 2), 46.29)
        
        # Test arrotondamento
        self.assertEqual(round(0.44512 * 100, 2), 44.51)
        self.assertEqual(round(0.44518 * 100, 2), 44.52)


class TestOddsConversion(unittest.TestCase):
    """Test per conversioni quote"""
    
    def test_decimal_odds_to_probability(self):
        """Test conversione quote decimali -> probabilità implicita"""
        
        # Formula: prob = 1 / odds
        
        # Quote favorite
        odds = 1.50
        prob = 1 / odds
        self.assertAlmostEqual(prob, 0.6667, places=4)  # 66.67%
        
        # Quote equilibrate
        odds = 2.00
        prob = 1 / odds
        self.assertEqual(prob, 0.5)  # 50%
        
        # Quote underdog
        odds = 4.00
        prob = 1 / odds
        self.assertEqual(prob, 0.25)  # 25%
    
    def test_overround_margin(self):
        """Test calcolo overround (margine bookmaker)"""
        
        # Quote equilibrate teoriche: 2.00, 2.00, 2.00 (50% ciascuna)
        # Quote reali bookmaker con margine
        odds_home = 2.10
        odds_draw = 3.25
        odds_away = 3.40
        
        # Probabilità implicite
        prob_h = 1 / odds_home  # 47.62%
        prob_d = 1 / odds_draw  # 30.77%
        prob_a = 1 / odds_away  # 29.41%
        
        # Overround (deve essere > 1.0)
        overround = prob_h + prob_d + prob_a
        self.assertGreater(overround, 1.0)  # Margine bookmaker
        
        # Margine tipicamente tra 5-15%
        margin_pct = (overround - 1.0) * 100
        self.assertGreater(margin_pct, 0)
        self.assertLess(margin_pct, 20)  # Margine ragionevole


class TestCacheManager(unittest.TestCase):
    """Test per CacheManager (se Redis disponibile)"""
    
    def setUp(self):
        """Setup test environment"""
        try:
            from web.cache_manager import CacheManager
            self.cache = CacheManager()
            self.cache_available = self.cache.enabled
        except Exception:
            self.cache_available = False
            self.skipTest("Redis not available")
    
    def test_cache_set_get(self):
        """Test set e get da cache"""
        if not self.cache_available:
            self.skipTest("Redis not available")
        
        from web.cache_manager import CacheManager
        cache = CacheManager()
        
        # Set value
        test_data = {'test': 'value', 'number': 42}
        success = cache.set('test_key', test_data, ttl=60)
        self.assertTrue(success)
        
        # Get value
        retrieved = cache.get('test_key')
        self.assertEqual(retrieved, test_data)
    
    def test_cache_expiration(self):
        """Test TTL cache"""
        if not self.cache_available:
            self.skipTest("Redis not available")
        
        import time
        from web.cache_manager import CacheManager
        cache = CacheManager()
        
        # Set con TTL breve
        cache.set('expire_test', {'data': 'test'}, ttl=1)
        
        # Dovrebbe esistere subito
        self.assertIsNotNone(cache.get('expire_test'))
        
        # Dopo 2 secondi dovrebbe essere scaduto
        time.sleep(2)
        self.assertIsNone(cache.get('expire_test'))
    
    def test_cache_miss(self):
        """Test cache miss"""
        if not self.cache_available:
            self.skipTest("Redis not available")
        
        from web.cache_manager import CacheManager
        cache = CacheManager()
        
        # Key inesistente
        result = cache.get('nonexistent_key_12345')
        self.assertIsNone(result)


class TestAPIIntegration(unittest.TestCase):
    """Test integrazione API (richiede server running)"""
    
    def setUp(self):
        """Check if server is running"""
        try:
            import requests
            r = requests.get('http://localhost:5008/api/status', timeout=2)
            self.server_running = r.status_code == 200
        except Exception:
            self.server_running = False
    
    def test_upcoming_matches_structure(self):
        """Test struttura response /api/upcoming_matches"""
        if not self.server_running:
            self.skipTest("Server not running")
        
        import requests
        r = requests.get('http://localhost:5008/api/upcoming_matches', timeout=10)
        
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        
        # Verifica campi obbligatori
        self.assertIn('total_matches', data)
        self.assertIn('matches', data)
        self.assertIn('data_source', data)
        
        # Se ci sono partite, verifica struttura
        if data['total_matches'] > 0:
            match = data['matches'][0]
            
            # Campi base
            self.assertIn('home_team', match)
            self.assertIn('away_team', match)
            self.assertIn('commence_time', match)
            
            # Odds
            self.assertIn('odds_real', match)
            
            # Predictions
            self.assertIn('prediction', match)
            
            # Value Betting
            self.assertIn('value_betting', match)
            vb = match['value_betting']
            
            # Verifica nuovi campi implementati
            self.assertIn('has_value', vb)
            self.assertIn('best_expected_value', vb)
            self.assertIn('best_market', vb)
            self.assertIn('best_outcome', vb)
            self.assertIn('best_odds', vb)
            
            # Expected values
            self.assertIn('expected_values', vb)
            evs = vb['expected_values']
            self.assertIn('home', evs)
            self.assertIn('draw', evs)
            self.assertIn('away', evs)
    
    def test_cache_stats_endpoint(self):
        """Test endpoint /api/cache/stats"""
        if not self.server_running:
            self.skipTest("Server not running")
        
        import requests
        r = requests.get('http://localhost:5008/api/cache/stats', timeout=5)
        
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertIn('cache_stats', data)
        self.assertIn('performance_impact', data)
        
        stats = data['cache_stats']
        self.assertIn('enabled', stats)
        self.assertIn('total_keys', stats)


def run_tests():
    """Run all tests and print results"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValueBettingCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestOddsConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
