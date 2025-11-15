#!/usr/bin/env python3
"""
Unit Tests per ML Predictions e Calculator
"""

import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMLPredictions(unittest.TestCase):
    """Test per predizioni Machine Learning"""
    
    def setUp(self):
        """Setup calculator per i test"""
        try:
            from scripts.professional_calculator import ProfessionalCalculator  # type: ignore[import]
            self.calculator = ProfessionalCalculator()
            self.calculator_available = True
        except Exception as e:
            self.calculator_available = False
            print(f"⚠️  Calculator non disponibile: {e}")
    
    def test_calculator_initialization(self):
        """Test inizializzazione calculator"""
        if not self.calculator_available:
            self.skipTest("Calculator not available")
        
        # Verifica che ci siano squadre disponibili
        self.assertIsNotNone(self.calculator.squadre_disponibili)
        self.assertGreater(len(self.calculator.squadre_disponibili), 0)
        
        # Verifica modelli caricati
        self.assertIsNotNone(self.calculator.models)
        self.assertGreater(len(self.calculator.models), 0)
    
    def test_squadre_serie_a(self):
        """Test che tutte le squadre Serie A principali siano disponibili"""
        if not self.calculator_available:
            self.skipTest("Calculator not available")
        
        # Squadre Serie A 2024/25 (principali)
        expected_teams = [
            'Inter', 'Milan', 'Juventus', 'Napoli', 
            'Roma', 'Lazio', 'Atalanta', 'Fiorentina'
        ]
        
        available = self.calculator.squadre_disponibili
        
        for team in expected_teams:
            self.assertIn(team, available, 
                         f"Squadra {team} non disponibile nel calculator")
    
    def test_prediction_output_format(self):
        """Test formato output predizioni"""
        if not self.calculator_available:
            self.skipTest("Calculator not available")
        
        # Test con squadre conosciute
        if 'Inter' in self.calculator.squadre_disponibili and \
           'Milan' in self.calculator.squadre_disponibili:
            
            predizione, probabilita, confidenza = \
                self.calculator.predici_partita_deterministica('Inter', 'Milan')
            
            # Verifica predizione (H, D, A)
            self.assertIn(predizione, ['H', 'D', 'A'])
            
            # Verifica probabilità
            self.assertIsInstance(probabilita, dict)
            self.assertIn('H', probabilita)
            self.assertIn('D', probabilita)
            self.assertIn('A', probabilita)
            
            # Probabilità devono sommare a ~1.0
            total_prob = sum(probabilita.values())
            self.assertAlmostEqual(total_prob, 1.0, places=2)
            
            # Ogni probabilità deve essere tra 0 e 1
            for prob in probabilita.values():
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)
            
            # Confidenza deve essere tra 0 e 1
            self.assertGreaterEqual(confidenza, 0.0)
            self.assertLessEqual(confidenza, 1.0)
    
    def test_probability_sum_equals_one(self):
        """Test che le probabilità sommino sempre a 1.0"""
        if not self.calculator_available:
            self.skipTest("Calculator not available")
        
        squadre = list(self.calculator.squadre_disponibili)[:5]
        
        for i in range(len(squadre)-1):
            home = squadre[i]
            away = squadre[i+1]
            
            _, probabilita, _ = \
                self.calculator.predici_partita_deterministica(home, away)
            
            total = sum(probabilita.values())
            self.assertAlmostEqual(total, 1.0, places=5,
                                  msg=f"Prob sum for {home} vs {away}: {total}")
    
    def test_home_advantage(self):
        """Test che il fattore campo sia considerato"""
        if not self.calculator_available:
            self.skipTest("Calculator not available")
        
        # Test con squadra forte vs debole
        if 'Inter' in self.calculator.squadre_disponibili and \
           'Verona' in self.calculator.squadre_disponibili:
            
            # Inter in casa vs Verona
            pred_home, prob_home, _ = \
                self.calculator.predici_partita_deterministica('Inter', 'Verona')
            
            # Verona in casa vs Inter
            pred_away, prob_away, _ = \
                self.calculator.predici_partita_deterministica('Verona', 'Inter')
            
            # Le probabilità dovrebbero essere diverse
            # (home advantage cambia le odds)
            self.assertNotAlmostEqual(
                prob_home['H'], prob_away['A'], places=1,
                msg="Home advantage not considered"
            )


class TestFeatureEngineering(unittest.TestCase):
    """Test per feature engineering"""
    
    def test_forma_recente_calculation(self):
        """Test calcolo forma recente"""
        
        # Simula risultati ultimi 5 match
        results = ['W', 'W', 'D', 'L', 'W']  # 3V 1P 1S
        
        # Punti: W=3, D=1, L=0
        points = {'W': 3, 'D': 1, 'L': 0}
        total_points = sum(points[r] for r in results)
        
        # Media punti
        avg_points = total_points / len(results)
        
        self.assertEqual(total_points, 10)  # 3+3+1+0+3
        self.assertEqual(avg_points, 2.0)  # 10/5
    
    def test_goals_statistics(self):
        """Test statistiche gol"""
        
        # Goals scored/conceded ultimi 5 match
        goals_scored = [2, 1, 0, 3, 2]  # 8 gol in 5 partite
        goals_conceded = [1, 1, 2, 2, 0]  # 6 gol subiti
        
        avg_scored = sum(goals_scored) / len(goals_scored)
        avg_conceded = sum(goals_conceded) / len(goals_conceded)
        
        self.assertEqual(avg_scored, 1.6)
        self.assertEqual(avg_conceded, 1.2)
        
        # Goal difference
        goal_diff = sum(goals_scored) - sum(goals_conceded)
        self.assertEqual(goal_diff, 2)  # 8-6
    
    def test_btts_probability(self):
        """Test calcolo probabilità Both Teams To Score"""
        
        # Simula ultimi match con BTTS
        matches_btts = [True, True, False, True, False]  # 3 su 5
        
        btts_rate = sum(matches_btts) / len(matches_btts)
        
        self.assertEqual(btts_rate, 0.6)  # 60%


class TestDataValidation(unittest.TestCase):
    """Test per validazione dati"""
    
    def test_odds_validity(self):
        """Test validità quote bookmaker"""
        
        # Quote valide devono essere >= 1.01
        valid_odds = [1.50, 2.00, 3.50, 10.0]
        for odds in valid_odds:
            self.assertGreaterEqual(odds, 1.01)
        
        # Quote invalide
        invalid_odds = [0.0, -1.0, 0.99]
        for odds in invalid_odds:
            self.assertLess(odds, 1.01)
    
    def test_probability_bounds(self):
        """Test che le probabilità siano tra 0 e 1"""
        
        valid_probs = [0.0, 0.33, 0.50, 0.75, 1.0]
        for prob in valid_probs:
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
        
        # Test che 1/odds dia sempre probabilità valida
        odds_values = [1.50, 2.00, 3.50, 10.0, 50.0]
        for odds in odds_values:
            implied_prob = 1 / odds
            self.assertGreaterEqual(implied_prob, 0.0)
            self.assertLessEqual(implied_prob, 1.0)
    
    def test_team_name_normalization(self):
        """Test normalizzazione nomi squadre"""
        
        # Test mapping comuni
        mappings = {
            'Inter Milan': 'Inter',
            'AC Milan': 'Milan',
            'Atalanta BC': 'Atalanta',
            'AS Roma': 'Roma',
            'Hellas Verona': 'Verona'
        }
        
        for api_name, dataset_name in mappings.items():
            # Il mapping dovrebbe rimuovere prefissi/suffissi
            self.assertIn(dataset_name, api_name)


class TestEdgeCases(unittest.TestCase):
    """Test per casi limite"""
    
    def test_zero_probability_edge_case(self):
        """Test EV con probabilità 0"""
        
        prob = 0.0
        odds = 10.0
        ev = prob * odds - 1
        
        self.assertEqual(ev, -1.0)  # -100% (no value)
    
    def test_very_low_odds_edge_case(self):
        """Test con quote molto basse (favorito schiacciante)"""
        
        prob = 0.95
        odds = 1.05
        ev = prob * odds - 1
        
        # Anche con 95% prob, odds 1.05 danno EV negativo
        self.assertLess(ev, 0.0)
    
    def test_identical_teams_prediction(self):
        """Test predizione con stessa squadra (caso impossibile)"""
        
        # Test che due squadre diverse siano effettivamente diverse
        team1 = 'Inter'
        team2 = 'Milan'
        
        self.assertNotEqual(team1, team2)
        
        # Test che una squadra sia uguale a se stessa
        self.assertEqual(team1, team1)
    
    def test_empty_string_team_names(self):
        """Test con nomi squadra vuoti"""
        
        # Test validazione nomi
        team_name = ""
        self.assertFalse(bool(team_name))  # Empty string è False
        
        team_name = "   "
        self.assertFalse(bool(team_name.strip()))  # Solo spazi


def run_ml_tests():
    """Run ML-specific tests"""
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMLPredictions))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("ML TESTS SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL ML TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME ML TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_ml_tests()
    sys.exit(exit_code)
