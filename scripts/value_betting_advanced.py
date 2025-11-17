"""
📊 VALUE BETTING ADVANCED SYSTEM
Sistema avanzato per identificare value bets tramite:
- Multi-bookmaker comparison (trova best odds)
- Closing Line Value (CLV) analysis
- Odds movement tracking (sharp money detection)
- Dynamic Kelly sizing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
from dataclasses import dataclass, field

@dataclass
class BookmakerOdds:
    """Container per odds di un bookmaker"""
    bookmaker: str
    home: float
    draw: float
    away: float
    timestamp: datetime
    margin: Optional[float] = None
    
    def __post_init__(self):
        # Calcola margine bookmaker
        if not self.margin:
            self.margin = (1/self.home + 1/self.draw + 1/self.away - 1) * 100

@dataclass
class ValueBet:
    """Container per una value bet identificata"""
    match: str
    prediction: str
    probability: float
    best_odds: float
    bookmaker: str
    expected_value: float
    kelly_stake: float
    clv_score: Optional[float] = None  # Closing Line Value
    odds_movement: Optional[str] = None  # "rising" / "falling" / "stable"
    sharp_money: bool = False
    score: float = field(default=0.0, init=False)  # Computed score for ranking


class ValueBettingSystem:
    def __init__(self):
        self.bookmakers_history = {}  # Track odds history
        self.sharp_thresholds = {
            'odds_movement': 0.10,  # 10% movement = significativo
            'volume_spike': 2.0,     # 2x volume normale
            'reverse_line': True     # Line si muove contro public money
        }
    
    def get_multi_bookmaker_odds(self, match_id: str, market: str = '1X2') -> List[BookmakerOdds]:
        """
        Recupera odds da múltipli bookmaker
        
        In produzione, usa API come:
        - The Odds API (odds-api.com)
        - RapidAPI Sports Odds
        - Betfair Exchange API
        """
        
        # MOCK DATA per development (sostituisci con API reale)
        mock_odds = [
            BookmakerOdds('Bet365', 2.10, 3.40, 3.50, datetime.now()),
            BookmakerOdds('Pinnacle', 2.15, 3.35, 3.45, datetime.now()),  # Sharp bookmaker
            BookmakerOdds('BetVictor', 2.05, 3.50, 3.60, datetime.now()),
            BookmakerOdds('1xBet', 2.20, 3.30, 3.40, datetime.now()),
            BookmakerOdds('Betway', 2.08, 3.45, 3.55, datetime.now()),
        ]
        
        return mock_odds
    
    def find_best_odds(self, odds_list: List[BookmakerOdds], outcome: str) -> Tuple[float, str]:
        """
        Trova le migliori odds per un dato outcome
        
        Args:
            odds_list: Lista di odds da vari bookmaker
            outcome: 'H', 'D', or 'A'
        
        Returns:
            (best_odds, bookmaker_name)
        """
        outcome_map = {'H': 'home', 'D': 'draw', 'A': 'away'}
        attr = outcome_map[outcome]
        
        best = max(odds_list, key=lambda x: getattr(x, attr))
        return getattr(best, attr), best.bookmaker
    
    def calculate_implied_probability(self, odds: float) -> float:
        """Probabilità implicita dalle odds (senza margine)"""
        return 1 / odds
    
    def calculate_true_odds(self, odds_list: List[BookmakerOdds]) -> Dict[str, float]:
        """
        Calcola "true odds" usando Pinnacle (sharp bookmaker) + average
        
        Pinnacle ha margini bassissimi (~2%) quindi più vicino al vero valore
        """
        pinnacle = next((b for b in odds_list if b.bookmaker == 'Pinnacle'), None)
        
        if pinnacle and pinnacle.margin is not None:
            # Usa Pinnacle come riferimento (rimuovi margine)
            margin_factor = 1 / (1 + pinnacle.margin/100)
            
            return {
                'H': 1 / (self.calculate_implied_probability(pinnacle.home) * margin_factor),
                'D': 1 / (self.calculate_implied_probability(pinnacle.draw) * margin_factor),
                'A': 1 / (self.calculate_implied_probability(pinnacle.away) * margin_factor)
            }
        else:
            # Fallback: usa media di tutti i bookmaker
            avg_home = float(np.mean([b.home for b in odds_list]))
            avg_draw = float(np.mean([b.draw for b in odds_list]))
            avg_away = float(np.mean([b.away for b in odds_list]))
            
            return {'H': avg_home, 'D': avg_draw, 'A': avg_away}
    
    def track_odds_movement(self, match_id: str, current_odds: List[BookmakerOdds]):
        """
        Traccia movimento odds nel tempo
        Identifica sharp money (soldi professionisti)
        """
        if match_id not in self.bookmakers_history:
            self.bookmakers_history[match_id] = []
        
        self.bookmakers_history[match_id].append({
            'timestamp': datetime.now(),
            'odds': current_odds
        })
    
    def calculate_odds_movement(self, match_id: str, outcome: str, 
                                lookback_hours: int = 24) -> Dict:
        """
        Analizza movimento odds nelle ultime N ore
        
        Returns:
            {
                'movement_pct': float,  # % change
                'direction': str,       # 'rising', 'falling', 'stable'
                'velocity': float,      # speed of change
                'sharp_detected': bool  # sharp money indicator
            }
        """
        if match_id not in self.bookmakers_history:
            return {'movement_pct': 0, 'direction': 'stable', 'velocity': 0, 'sharp_detected': False}
        
        history = self.bookmakers_history[match_id]
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        recent = [h for h in history if h['timestamp'] >= cutoff]
        
        if len(recent) < 2:
            return {'movement_pct': 0, 'direction': 'stable', 'velocity': 0, 'sharp_detected': False}
        
        # Prendi Pinnacle odds (sharp bookmaker)
        outcome_map = {'H': 'home', 'D': 'draw', 'A': 'away'}
        attr = outcome_map[outcome]
        
        first_pinnacle = next((b for b in recent[0]['odds'] if b.bookmaker == 'Pinnacle'), None)
        last_pinnacle = next((b for b in recent[-1]['odds'] if b.bookmaker == 'Pinnacle'), None)
        
        if not first_pinnacle or not last_pinnacle:
            return {'movement_pct': 0, 'direction': 'stable', 'velocity': 0, 'sharp_detected': False}
        
        first_odds = getattr(first_pinnacle, attr)
        last_odds = getattr(last_pinnacle, attr)
        
        movement_pct = (last_odds - first_odds) / first_odds
        velocity = movement_pct / (len(recent) - 1)  # Movement per snapshot
        
        direction = 'stable'
        if abs(movement_pct) > self.sharp_thresholds['odds_movement']:
            direction = 'rising' if movement_pct > 0 else 'falling'
        
        # Sharp money detection: odds scendono ma dovrebbero salire (reverse line movement)
        sharp_detected = direction == 'falling' and abs(movement_pct) > self.sharp_thresholds['odds_movement']
        
        return {
            'movement_pct': movement_pct * 100,
            'direction': direction,
            'velocity': velocity,
            'sharp_detected': sharp_detected
        }
    
    def calculate_closing_line_value(self, bet_odds: float, closing_odds: float) -> float:
        """
        Calcola CLV (Closing Line Value)
        
        CLV positivo = hai preso odds migliori della chiusura (good!)
        CLV è il miglior indicatore di long-term profitability
        
        Formula: CLV = (bet_odds / closing_odds) - 1
        """
        return ((bet_odds / closing_odds) - 1) * 100
    
    def identify_value_bets(self, 
                           prediction: str,
                           model_probability: float,
                           match_id: str,
                           current_odds: List[BookmakerOdds],
                           min_ev: float = 0.05,
                           min_clv: float = 0.02) -> Optional[ValueBet]:
        """
        Identifica value bet combinando:
        1. Model probability vs best market odds
        2. Odds movement analysis
        3. CLV estimation
        
        Returns:
            ValueBet object o None
        """
        
        # 1. Trova best odds disponibili
        best_odds, bookmaker = self.find_best_odds(current_odds, prediction)
        
        # 2. Calcola Expected Value
        ev = (model_probability * best_odds) - 1
        
        if ev < min_ev:
            return None  # No value
        
        # 3. Calcola true market odds (Pinnacle reference)
        true_odds = self.calculate_true_odds(current_odds)
        true_odd = true_odds[prediction]
        
        # 4. Analizza movimento odds
        movement = self.calculate_odds_movement(match_id, prediction)
        
        # 5. Stima CLV (usando true odds come proxy per closing)
        clv = self.calculate_closing_line_value(best_odds, true_odd)
        
        if clv < min_clv and not movement['sharp_detected']:
            return None  # No edge
        
        # 6. Dynamic Kelly sizing (più conservativo se CLV basso)
        kelly_fraction = 0.125  # Base: 1/8 Kelly
        
        # Boost Kelly se:
        # - CLV positivo e alto
        # - Sharp money detected
        # - Odds rising (più value)
        if clv > 5.0:
            kelly_fraction *= 1.5  # 1.5x sizing
        if movement['sharp_detected']:
            kelly_fraction *= 1.3
        if movement['direction'] == 'rising':
            kelly_fraction *= 1.2
        
        # Kelly formula
        b = best_odds - 1
        p = model_probability
        q = 1 - p
        kelly = (b * p - q) / b
        kelly_stake = max(0, min(kelly * kelly_fraction, 0.05))  # Cap 5%
        
        # Create value bet
        return ValueBet(
            match=match_id,
            prediction=prediction,
            probability=model_probability,
            best_odds=best_odds,
            bookmaker=bookmaker,
            expected_value=ev,
            kelly_stake=kelly_stake,
            clv_score=clv,
            odds_movement=movement['direction'],
            sharp_money=movement['sharp_detected']
        )
    
    def rank_value_bets(self, bets: List[ValueBet]) -> List[ValueBet]:
        """
        Rankizza value bets per qualità
        
        Score = EV * CLV * Sharp_multiplier * Probability
        """
        for bet in bets:
            sharp_mult = 1.5 if bet.sharp_money else 1.0
            clv_factor = (1 + bet.clv_score/100) if bet.clv_score is not None else 1.0
            bet.score = (
                bet.expected_value * 100 *  # EV%
                clv_factor *                # CLV factor
                sharp_mult *                # Sharp bonus
                bet.probability             # Confidence
            )
        
        return sorted(bets, key=lambda x: x.score, reverse=True)


# Example usage
if __name__ == "__main__":
    print("🎯 VALUE BETTING ADVANCED SYSTEM\n")
    
    system = ValueBettingSystem()
    
    # Simula una partita
    match_id = "2024-11-17_Inter_Napoli"
    
    # Get odds da multiple bookmakers
    odds = system.get_multi_bookmaker_odds(match_id)
    
    print("📊 Multi-bookmaker odds:")
    for odd in odds:
        print(f"   {odd.bookmaker:12} H:{odd.home:.2f} D:{odd.draw:.2f} A:{odd.away:.2f} (margin: {odd.margin:.1f}%)")
    
    # Track movement
    system.track_odds_movement(match_id, odds)
    
    # Simula predizione modello
    model_prediction = 'H'
    model_probability = 0.55
    
    print(f"\n🤖 Model Prediction: {model_prediction} ({model_probability*100:.1f}%)")
    
    # Identifica value bet
    value_bet = system.identify_value_bets(
        prediction=model_prediction,
        model_probability=model_probability,
        match_id=match_id,
        current_odds=odds,
        min_ev=0.03,
        min_clv=0.01
    )
    
    if value_bet:
        print(f"\n✅ VALUE BET FOUND!")
        print(f"   Match: {value_bet.match}")
        print(f"   Prediction: {value_bet.prediction} @ {value_bet.best_odds:.2f} ({value_bet.bookmaker})")
        print(f"   Probability: {value_bet.probability*100:.1f}%")
        print(f"   Expected Value: {value_bet.expected_value*100:+.2f}%")
        print(f"   CLV Score: {value_bet.clv_score:+.2f}%")
        print(f"   Kelly Stake: {value_bet.kelly_stake*100:.2f}% of bankroll")
        print(f"   Odds Movement: {value_bet.odds_movement}")
        if value_bet.sharp_money:
            print(f"   🔥 SHARP MONEY DETECTED!")
    else:
        print(f"\n❌ No value bet found")
    
    print("\n" + "="*70)
    print("💡 Integration Tips:")
    print("   1. Connect real odds API (The Odds API, RapidAPI)")
    print("   2. Track odds every 1-2 hours before match")
    print("   3. Alert when CLV >3% + sharp money")
    print("   4. Use Pinnacle as benchmark (lowest margins)")
    print("   5. Focus on closing line value (best predictor)")
