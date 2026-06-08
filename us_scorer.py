"""
US Stock Scorer - Finnhub ONLY
No yfinance dependency - uses only Finnhub API
Scores based on keywords + Finnhub data
"""

import requests
import os
import time
from dotenv import load_dotenv

# Import configurable keywords
try:
    from keywords_config import (
        get_primary_keywords,
        get_industry_keywords,
        get_tailwind_keywords,
        get_sector_name
    )
except ImportError:
    def get_primary_keywords():
        return ['defense', 'government', 'military', 'contract']
    def get_industry_keywords():
        return ['defense', 'aerospace', 'security']
    def get_tailwind_keywords():
        return ['defense', 'ai', 'space']
    def get_sector_name():
        return "Defense (default)"

load_dotenv()

class USStockScorer:
    """Score US stocks using FINNHUB ONLY"""
    
    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_KEY', '')
        self.finnhub_base = "https://finnhub.io/api/v1"
        
        # Get keywords from config
        self.primary_keywords = get_primary_keywords()
        self.industry_keywords = get_industry_keywords()
        self.tailwind_keywords = get_tailwind_keywords()
        self.sector_name = get_sector_name()
        
        self.min_delay = 0.05
        
        if not self.finnhub_key:
            print("⚠️  WARNING: FINNHUB_KEY not found!")
        else:
            print(f"✅ Scorer initialized for: {self.sector_name}")
    
    def score_stock(self, symbol):
        """
        Score using FINNHUB data only
        ALWAYS returns a dict with scores
        """
        
        try:
            time.sleep(self.min_delay)
            
            # Get company profile from Finnhub (MAIN DATA SOURCE)
            profile = self._get_company_profile(symbol)
            
            if not profile:
                # Return minimal score if no data
                return self._create_fallback_score(symbol)
            
            # Get metrics from Finnhub
            metrics = self._get_financial_metrics(symbol)
            
            scores = {}
            
            # Score on 7 reasons
            scores['sector_focus'] = self._score_sector_focus(symbol, profile)
            scores['industry_match'] = self._score_industry_match(symbol, profile)
            scores['keyword_strength'] = self._score_keyword_strength(symbol, profile)
            scores['tailwind'] = self._score_tailwind(symbol, profile)
            scores['growth_potential'] = self._score_growth_potential(metrics)
            scores['profitability'] = self._score_profitability(metrics)
            scores['execution'] = self._score_execution(profile)
            
            # Calculate totals
            total_score = sum(scores.values())
            scores['total_score'] = total_score
            scores['rating'] = self._get_rating(total_score)
            
            # Add metrics
            scores['symbol'] = symbol
            scores['company_name'] = profile.get('name', symbol)
            scores['exchange'] = profile.get('exchange', 'UNKNOWN')
            scores['sector'] = profile.get('sector', '')
            scores['industry'] = profile.get('industry', '')
            scores['current_price'] = profile.get('lastPrice', 0)
            scores['market_cap'] = profile.get('marketCapitalization', 0)
            scores['pe_ratio'] = profile.get('pe', 0)
            
            return scores
            
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")
            return self._create_fallback_score(symbol)
    
    def _get_company_profile(self, symbol):
        """Get company profile from Finnhub"""
        
        try:
            url = f"{self.finnhub_base}/stock/profile2"
            params = {'symbol': symbol, 'token': self.finnhub_key}
            
            resp = requests.get(url, params=params, timeout=3)
            
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    return data
            
            return None
        except Exception as e:
            return None
    
    def _get_financial_metrics(self, symbol):
        """Get financial metrics from Finnhub"""
        
        try:
            url = f"{self.finnhub_base}/stock/metric"
            params = {
                'symbol': symbol,
                'metric': 'all',
                'token': self.finnhub_key
            }
            
            resp = requests.get(url, params=params, timeout=3)
            
            if resp.status_code == 200:
                data = resp.json()
                if 'metric' in data:
                    return data['metric']
            
            return {}
        except:
            return {}
    
    def _score_sector_focus(self, symbol, profile):
        """Score 1: Sector Focus (0-3)"""
        
        score = 0.5
        
        try:
            # Get description
            description = (profile.get('description', '') or '').lower()
            name = (profile.get('name', '') or '').lower()
            
            # Count keyword matches
            keyword_count = sum(1 for kw in self.primary_keywords 
                              if kw.lower() in description or kw.lower() in name)
            
            if keyword_count >= 4:
                score = 3.0
            elif keyword_count >= 2:
                score = 2.5
            elif keyword_count >= 1:
                score = 1.5
            else:
                score = 0.5
            
            # Check sector
            sector = (profile.get('sector', '') or '').lower()
            
            sector_match = any(ind.lower() in sector for ind in self.industry_keywords)
            
            if sector_match:
                score = min(score + 0.5, 3.0)
            
            return score
        except:
            return 0.5
    
    def _score_industry_match(self, symbol, profile):
        """Score 2: Industry Match (0-3)"""
        
        score = 0
        
        try:
            industry = (profile.get('industry', '') or '').lower()
            description = (profile.get('description', '') or '').lower()
            
            # Check industry keywords
            industry_matches = sum(1 for ind in self.industry_keywords 
                                  if ind.lower() in industry or ind.lower() in description)
            
            if industry_matches >= 3:
                score = 3.0
            elif industry_matches >= 2:
                score = 2.5
            elif industry_matches >= 1:
                score = 2.0
            
            return score
        except:
            return 0
    
    def _score_keyword_strength(self, symbol, profile):
        """Score 3: Keyword Strength (0-2)"""
        
        score = 0
        
        try:
            description = (profile.get('description', '') or '').lower()
            name = (profile.get('name', '') or '').lower()
            
            all_text = description + ' ' + name
            
            # Count total keyword matches
            total_matches = sum(1 for kw in self.primary_keywords + self.industry_keywords 
                              if kw.lower() in all_text)
            
            if total_matches >= 5:
                score = 2.0
            elif total_matches >= 3:
                score = 1.5
            elif total_matches >= 1:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_tailwind(self, symbol, profile):
        """Score 4: Industry Tailwinds (0-2)"""
        
        score = 0
        
        try:
            industry = (profile.get('industry', '') or '').lower()
            description = (profile.get('description', '') or '').lower()
            
            # Count tailwind matches
            tailwind_matches = sum(1 for d in self.tailwind_keywords 
                                  if d.lower() in industry or d.lower() in description)
            
            if tailwind_matches >= 3:
                score = 2.0
            elif tailwind_matches >= 2:
                score = 1.5
            elif tailwind_matches >= 1:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_growth_potential(self, metrics):
        """Score 5: Growth Potential (0-2)"""
        
        score = 0
        
        try:
            if not metrics:
                return 0
            
            revenue_growth = metrics.get('revenueGrowth5Y', 0) or metrics.get('revenueGrowth', 0)
            
            if revenue_growth and revenue_growth >= 0.25:
                score = 2.0
            elif revenue_growth and revenue_growth >= 0.15:
                score = 1.5
            elif revenue_growth and revenue_growth >= 0.05:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_profitability(self, metrics):
        """Score 6: Profitability (0-1.5)"""
        
        score = 0
        
        try:
            if not metrics:
                return 0
            
            # Try net margin
            net_margin = metrics.get('netMargin', 0) or metrics.get('profitMargin', 0)
            
            if net_margin and net_margin > 0:
                if net_margin > 0.12:
                    score = 1.5
                elif net_margin > 0.08:
                    score = 1.2
                elif net_margin > 0.03:
                    score = 0.8
                elif net_margin > 0:
                    score = 0.4
            
            # Try ROA
            if score == 0:
                roa = metrics.get('roa', 0)
                if roa and roa > 0.05:
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _score_execution(self, profile):
        """Score 7: Execution (0-1.0)"""
        
        score = 0
        
        try:
            # Check if company exists and has market cap
            market_cap = profile.get('marketCapitalization', 0)
            
            if market_cap and market_cap > 0:
                score = 0.5
                
                if market_cap > 1_000_000_000:  # > $1B
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _create_fallback_score(self, symbol):
        """Create fallback score"""
        return {
            'symbol': symbol,
            'total_score': 0.5,
            'rating': '👀 WATCH',
            'sector_focus': 0.5,
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
    
    def get_rating(self, score):
        """Public method"""
        return self._get_rating(score)
