"""
US Stock Scorer - Hardcoded Sector Mapping
Zero API dependencies - uses predefined sector lists
Fast, reliable, always works
"""

import time
from dotenv import load_dotenv

# Import configurable keywords
try:
    from keywords_config import get_sector_name
except ImportError:
    def get_sector_name():
        return "Defense (default)"

load_dotenv()

class USStockScorer:
    """Score US stocks using hardcoded sector lists"""
    
    def __init__(self):
        self.sector_name = get_sector_name()
        print(f"✅ Scorer initialized for: {self.sector_name}")
        
        # DEFENSE/GOVERNMENT CONTRACTORS (HIGH PRIORITY)
        self.defense_primary = [
            'KTOS', 'LDOS', 'LHX', 'RTX', 'LMT', 'GD', 'NOC', 'HII',
            'SAIC', 'CACI', 'AVAV', 'VSAT', 'MAXR', 'AERI', 'EACL'
        ]
        
        # AI/DEFENSE HYBRID (MEDIUM-HIGH)
        self.ai_defense = ['BBAI', 'PLTR', 'TENB', 'CRWD', 'PANW']
        
        # SPACE/AEROSPACE (MEDIUM-HIGH)
        self.space = ['RKLB', 'ROCKET', 'MAXR', 'AERI', 'VSAT']
        
        # LARGE CAP TECH (MEDIUM)
        self.large_cap_tech = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN', 'TSLA']
        
        # OTHER TECH (LOW-MEDIUM)
        self.other_tech = ['AMD', 'INTC', 'QCOM', 'CRWD', 'PANW', 'NET', 'DDOG', 'SNOW', 'NOW']
        
        # INDUSTRIAL/MANUFACTURING (LOW-MEDIUM)
        self.industrial = ['BA', 'CAT', 'DE', 'MMM', 'PCAR']
        
        # SMALL CAP / SPECULATIVE
        self.speculative = ['BBAI', 'RKLB', 'LCID', 'PLTR', 'COIN', 'UPST']
    
    def score_stock(self, symbol):
        """
        Score based on hardcoded sector mapping
        ALWAYS returns a dict with 0-14 score
        """
        
        try:
            score = self._calculate_score(symbol)
            
            return {
                'symbol': symbol,
                'total_score': score,
                'rating': self._get_rating(score),
                'sector_focus': self._get_sector_score(symbol),
                'industry_match': self._get_industry_score(symbol),
                'keyword_strength': self._get_strength_score(symbol),
                'tailwind': self._get_tailwind_score(symbol),
                'growth_potential': 1.0,
                'profitability': 0.5,
                'execution': 0.5,
                'company_name': symbol,
                'exchange': 'NASDAQ/NYSE',
                'sector': self._get_sector_name(symbol),
                'industry': self._get_industry_name(symbol),
                'current_price': 0,
                'market_cap': 0,
                'pe_ratio': 0
            }
            
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")
            return self._create_fallback_score(symbol)
    
    def _calculate_score(self, symbol):
        """Calculate 0-14 score based on sector"""
        
        score = 0.0
        
        # TIER 1: Defense/Government Contractors (10-14 points)
        if symbol in self.defense_primary:
            score = 12.0  # High defense relevance
        
        # TIER 2: AI/Defense Hybrid (9-11 points)
        elif symbol in self.ai_defense:
            score = 10.0  # Defense + AI
        
        # TIER 3: Space/Aerospace (8-10 points)
        elif symbol in self.space:
            score = 9.0  # Space focus
        
        # TIER 4: Large Cap Tech (5-7 points)
        elif symbol in self.large_cap_tech:
            score = 6.0  # Tech exposure
        
        # TIER 5: Other Tech (4-6 points)
        elif symbol in self.other_tech:
            score = 5.0  # Tech play
        
        # TIER 6: Industrial (3-5 points)
        elif symbol in self.industrial:
            score = 4.0  # Industrial
        
        # TIER 7: Speculative (2-4 points)
        elif symbol in self.speculative:
            score = 3.0  # High risk/reward
        
        # DEFAULT: Unknown (1 point minimum)
        else:
            score = 1.0  # Baseline
        
        return score
    
    def _get_sector_score(self, symbol):
        """Get sector focus score (0-3)"""
        if symbol in self.defense_primary:
            return 3.0
        elif symbol in self.ai_defense:
            return 2.5
        elif symbol in self.space:
            return 2.5
        elif symbol in self.large_cap_tech:
            return 1.5
        else:
            return 0.5
    
    def _get_industry_score(self, symbol):
        """Get industry match score (0-3)"""
        if symbol in self.defense_primary:
            return 3.0
        elif symbol in self.ai_defense:
            return 2.5
        elif symbol in self.space:
            return 2.0
        elif symbol in self.large_cap_tech:
            return 1.5
        else:
            return 0.5
    
    def _get_strength_score(self, symbol):
        """Get keyword strength score (0-2)"""
        if symbol in self.defense_primary:
            return 2.0
        elif symbol in self.ai_defense:
            return 1.5
        elif symbol in self.space:
            return 1.5
        else:
            return 0.5
    
    def _get_tailwind_score(self, symbol):
        """Get tailwind score (0-2)"""
        if symbol in self.defense_primary:
            return 2.0
        elif symbol in self.ai_defense:
            return 1.5
        elif symbol in self.space:
            return 1.5
        else:
            return 0.5
    
    def _get_sector_name(self, symbol):
        """Get sector for symbol"""
        if symbol in self.defense_primary:
            return "Defense"
        elif symbol in self.ai_defense:
            return "AI/Defense"
        elif symbol in self.space:
            return "Space/Aerospace"
        elif symbol in self.large_cap_tech:
            return "Large Cap Tech"
        elif symbol in self.industrial:
            return "Industrial"
        else:
            return "Technology"
    
    def _get_industry_name(self, symbol):
        """Get industry for symbol"""
        if symbol in self.defense_primary:
            return "Defense Contractors"
        elif symbol in self.ai_defense:
            return "AI/Cybersecurity"
        elif symbol in self.space:
            return "Space/Satellite"
        elif symbol in self.large_cap_tech:
            return "Technology"
        else:
            return "Various"
    
    def _get_rating(self, score):
        """Convert score to rating"""
        if score >= 12:
            return "🚀 STRONG BUY"
        elif score >= 10:
            return "⭐ BUY"
        elif score >= 8:
            return "📈 BUY"
        elif score >= 6:
            return "⏸ HOLD"
        elif score >= 4:
            return "👀 WATCH"
        else:
            return "❌ AVOID"
    
    def _create_fallback_score(self, symbol):
        """Create fallback score"""
        return {
            'symbol': symbol,
            'total_score': 1.0,
            'rating': '❌ AVOID',
            'sector_focus': 0,
            'industry_match': 0,
            'keyword_strength': 0,
            'tailwind': 0,
            'growth_potential': 0,
            'profitability': 0,
            'execution': 0,
            'company_name': symbol,
            'exchange': 'UNKNOWN',
            'sector': '',
            'industry': '',
            'current_price': 0,
            'market_cap': 0,
            'pe_ratio': 0
        }
    
    def get_rating(self, score):
        """Public method"""
        return self._get_rating(score)
