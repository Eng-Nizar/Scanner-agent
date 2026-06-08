"""
US Stock Scorer - Ultra-Simple Version
Keyword-focused scoring that always works
No dependencies on yfinance full data
"""

import yfinance as yf
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
    """Score US stocks - Simple keyword-based approach"""
    
    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_KEY', '')
        self.finnhub_base = "https://finnhub.io/api/v1"
        
        # Get keywords from config
        self.primary_keywords = get_primary_keywords()
        self.industry_keywords = get_industry_keywords()
        self.tailwind_keywords = get_tailwind_keywords()
        self.sector_name = get_sector_name()
        
        self.min_delay = 0.05
        
        print(f"✅ Scorer initialized for: {self.sector_name}")
    
    def score_stock(self, symbol):
        """
        Score a US stock (0-14 scale)
        Simple, keyword-focused, ALWAYS returns a dict
        """
        
        try:
            time.sleep(self.min_delay)
            
            # Get minimal info from yfinance
            info = self._get_minimal_info(symbol)
            
            # Try Finnhub data (optional)
            finnhub_data = self._get_finnhub_data_safe(symbol)
            
            scores = {}
            
            # Score on 7 reasons
            scores['sector_focus'] = self._score_sector_focus(symbol, info, finnhub_data)
            scores['industry_match'] = self._score_industry_match(symbol, info, finnhub_data)
            scores['keyword_strength'] = self._score_keyword_strength(symbol, info, finnhub_data)
            scores['tailwind'] = self._score_tailwind(symbol, info, finnhub_data)
            scores['growth_potential'] = self._score_growth_potential(info, finnhub_data)
            scores['profitability'] = self._score_profitability(info, finnhub_data)
            scores['execution'] = self._score_execution_simple(symbol)
            
            # Calculate totals
            total_score = sum(scores.values())
            scores['total_score'] = total_score
            scores['rating'] = self._get_rating(total_score)
            
            # Add metrics
            scores['symbol'] = symbol
            scores['company_name'] = info.get('longName', symbol)
            scores['exchange'] = info.get('exchange', 'UNKNOWN')
            scores['sector'] = info.get('sector', '')
            scores['industry'] = info.get('industry', '')
            scores['current_price'] = info.get('currentPrice', 0)
            scores['market_cap'] = info.get('marketCap', 0)
            scores['pe_ratio'] = info.get('trailingPE', 0)
            
            return scores
            
        except Exception as e:
            # Fallback: Return basic score
            return self._create_fallback_score(symbol)
    
    def _get_minimal_info(self, symbol):
        """Get MINIMAL info from yfinance (just basics)"""
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got SOME data (even if incomplete)
            if info:
                return {
                    'longName': info.get('longName', symbol),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'longBusinessSummary': info.get('longBusinessSummary', ''),
                    'currentPrice': info.get('currentPrice', 0),
                    'marketCap': info.get('marketCap', 0),
                    'trailingPE': info.get('trailingPE', 0),
                    'revenueGrowth': info.get('revenueGrowth', 0),
                    'exchange': info.get('exchange', 'UNKNOWN')
                }
            else:
                return self._create_empty_info(symbol)
                
        except Exception as e:
            print(f"  ⚠️  {symbol}: Could not get full data")
            return self._create_empty_info(symbol)
    
    def _create_empty_info(self, symbol):
        """Create empty info dict"""
        return {
            'longName': symbol,
            'sector': '',
            'industry': '',
            'longBusinessSummary': '',
            'currentPrice': 0,
            'marketCap': 0,
            'trailingPE': 0,
            'revenueGrowth': 0,
            'exchange': 'UNKNOWN'
        }
    
    def _get_finnhub_data_safe(self, symbol):
        """Get Finnhub data optionally"""
        
        try:
            if not self.finnhub_key:
                return {}
            
            profile = {}
            
            try:
                url = f"{self.finnhub_base}/stock/profile2"
                params = {'symbol': symbol, 'token': self.finnhub_key}
                resp = requests.get(url, params=params, timeout=2)
                
                if resp.status_code == 200:
                    profile = resp.json() or {}
            except:
                pass
            
            return {'profile': profile}
        
        except:
            return {}
    
    def _score_sector_focus(self, symbol, info, finnhub_data):
        """Score 1: Sector Focus - PRIMARY (0-3)"""
        
        score = 0.5  # Minimum baseline
        
        try:
            # Get description
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            if finnhub_data and 'profile' in finnhub_data:
                profile = finnhub_data['profile']
                description += ' ' + (profile.get('description', '') or '').lower()
            
            name = (info.get('longName', '') or '').lower()
            
            # Count keyword matches
            keyword_count = sum(1 for kw in self.primary_keywords 
                              if kw.lower() in description or kw.lower() in name)
            
            if keyword_count >= 4:
                score = 3.0
            elif keyword_count >= 2:
                score = 2.5
            elif keyword_count >= 1:
                score = 1.5
            
            # Boost for sector
            sector = (info.get('sector', '') or '').lower()
            industry = (info.get('industry', '') or '').lower()
            
            sector_match = any(ind.lower() in sector or ind.lower() in industry 
                             for ind in self.industry_keywords)
            
            if sector_match:
                score = min(score + 0.5, 3.0)
            
            return score
        except:
            return 0.5
    
    def _score_industry_match(self, symbol, info, finnhub_data):
        """Score 2: Industry Match (0-3)"""
        
        score = 0
        
        try:
            industry = (info.get('industry', '') or '').lower()
            sector = (info.get('sector', '') or '').lower()
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            # Check industry keywords
            industry_matches = sum(1 for ind in self.industry_keywords 
                                  if ind.lower() in industry or ind.lower() in description)
            
            if industry_matches >= 3:
                score = 3.0
            elif industry_matches >= 2:
                score = 2.5
            elif industry_matches >= 1:
                score = 2.0
            elif sector in ['technology', 'industrials', 'healthcare']:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_keyword_strength(self, symbol, info, finnhub_data):
        """Score 3: Keyword Strength (0-2)"""
        
        score = 0
        
        try:
            description = (info.get('longBusinessSummary', '') or '').lower()
            name = (info.get('longName', '') or '').lower()
            
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
    
    def _score_tailwind(self, symbol, info, finnhub_data):
        """Score 4: Industry Tailwinds (0-2)"""
        
        score = 0
        
        try:
            industry = (info.get('industry', '') or '').lower()
            description = (info.get('longBusinessSummary', '') or '').lower()
            
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
    
    def _score_growth_potential(self, info, finnhub_data):
        """Score 5: Growth Potential (0-2)"""
        
        score = 0
        
        try:
            # Check revenue growth
            revenue_growth = info.get('revenueGrowth', 0)
            
            if revenue_growth and revenue_growth >= 0.25:
                score = 2.0
            elif revenue_growth and revenue_growth >= 0.15:
                score = 1.5
            elif revenue_growth and revenue_growth >= 0.05:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_profitability(self, info, finnhub_data):
        """Score 6: Profitability (0-1.5)"""
        
        score = 0
        
        try:
            pe_ratio = info.get('trailingPE', 0)
            
            if pe_ratio and pe_ratio > 0:
                if pe_ratio < 20:
                    score = 1.5
                elif pe_ratio < 30:
                    score = 1.0
                elif pe_ratio < 50:
                    score = 0.5
            
            return score
        except:
            return 0
    
    def _score_execution_simple(self, symbol):
        """Score 7: Execution (0-1.0) - SIMPLE"""
        
        score = 0
        
        try:
            # Just check if stock exists and has a price
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info and info.get('currentPrice') and info.get('currentPrice') > 0:
                score = 0.5  # Existing + trading = baseline
                
                # Try to get market cap as size indicator
                market_cap = info.get('marketCap', 0)
                if market_cap > 1_000_000_000:  # >$1B
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _create_fallback_score(self, symbol):
        """Create fallback score when everything fails"""
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
