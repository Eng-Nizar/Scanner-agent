"""
US Stock Scorer - Configurable by Sector
Uses keywords_config.py for flexible sector switching
Defense, Space, AI, Cybersecurity, Biotech, etc.
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
    print("⚠️ keywords_config.py not found, using default defense keywords")
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
    """Score US stocks - Configurable by sector"""
    
    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_KEY', '')
        self.finnhub_base = "https://finnhub.io/api/v1"
        
        # Get keywords from config (can be switched at runtime)
        self.primary_keywords = get_primary_keywords()
        self.industry_keywords = get_industry_keywords()
        self.tailwind_keywords = get_tailwind_keywords()
        self.sector_name = get_sector_name()
        
        self.last_request_time = 0
        self.min_delay = 0.1  # Delay between requests
        
        print(f"✅ Scorer initialized for: {self.sector_name}")
    
    def score_stock(self, symbol):
        """
        Score a US stock (0-14 scale)
        Uses keywords from keywords_config.py
        ALWAYS returns a dict, NEVER returns None
        """
        
        try:
            # Add small delay to avoid rate limits
            time.sleep(self.min_delay)
            
            # Get basic info from yfinance
            info = self._get_stock_info_safe(symbol)
            
            if not info:
                # Fallback: Create minimal info dict
                info = {
                    'longName': symbol,
                    'sector': '',
                    'industry': '',
                    'longBusinessSummary': '',
                    'currentPrice': 0,
                    'marketCap': 0,
                    'trailingPE': 0,
                    'exchange': 'UNKNOWN'
                }
            
            # Try to get Finnhub data (optional)
            finnhub_data = self._get_finnhub_data_safe(symbol)
            
            scores = {}
            
            # Score on 7 reasons - CONFIGURABLE BY SECTOR
            scores['sector_focus'] = self._score_sector_focus(symbol, info, finnhub_data)
            scores['industry_match'] = self._score_industry_match(symbol, info, finnhub_data)
            scores['backlog'] = self._score_backlog(info, finnhub_data)
            scores['revenue_growth'] = self._score_revenue_growth(info, finnhub_data)
            scores['profitability'] = self._score_profitability(info, finnhub_data)
            scores['tailwind'] = self._score_tailwind(symbol, info, finnhub_data)
            scores['execution'] = self._score_execution(symbol)
            
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
            scores['sector_focus'] = self.sector_name
            
            # ALWAYS return scores dict
            return scores
            
        except Exception as e:
            # Last resort: Return basic zero score
            print(f"Warning: Could not score {symbol} fully: {e}")
            return {
                'symbol': symbol,
                'total_score': 0.5,
                'rating': '👀 WATCH - POTENTIAL',
                'sector_focus': 0.5,
                'industry_match': 0,
                'backlog': 0,
                'revenue_growth': 0,
                'profitability': 0,
                'tailwind': 0,
                'execution': 0,
                'company_name': symbol,
                'exchange': 'UNKNOWN',
                'sector': '',
                'industry': '',
                'current_price': 0,
                'market_cap': 0,
                'pe_ratio': 0,
                'sector_focus': self.sector_name
            }
    
    def _get_stock_info_safe(self, symbol):
        """Get stock info from yfinance, handle rate limits"""
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info and info.get('currentPrice'):
                return info
            else:
                return None
                
        except Exception as e:
            print(f"  ⚠️  {symbol}: Rate limit (continuing)")
            return None
    
    def _get_finnhub_data_safe(self, symbol):
        """Get Finnhub data, won't fail the scan"""
        
        try:
            if not self.finnhub_key:
                return {}
            
            profile = {}
            metrics = {}
            
            # Try to get profile
            try:
                url = f"{self.finnhub_base}/stock/profile2"
                params = {'symbol': symbol, 'token': self.finnhub_key}
                resp = requests.get(url, params=params, timeout=2)
                
                if resp.status_code == 200:
                    profile = resp.json() or {}
            except:
                pass
            
            # Try to get metrics
            try:
                url = f"{self.finnhub_base}/stock/metric"
                params = {'symbol': symbol, 'metric': 'all', 'token': self.finnhub_key}
                resp = requests.get(url, params=params, timeout=2)
                
                if resp.status_code == 200:
                    metrics = resp.json().get('metric', {})
            except:
                pass
            
            return {'profile': profile, 'metrics': metrics}
        
        except:
            return {}
    
    def _score_sector_focus(self, symbol, info, finnhub_data):
        """Score 1: Sector Focus - PRIMARY SCORING (0-3)"""
        
        score = 0
        
        try:
            # Get description from both sources
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            if finnhub_data and 'profile' in finnhub_data:
                profile = finnhub_data['profile']
                description += ' ' + (profile.get('description', '') or '').lower()
            
            name = (info.get('longName', '') or '').lower()
            
            # Count keyword matches using configurable keywords
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
            
            # Boost if sector matches
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
            
            # Check if any industry keywords match
            industry_matches = sum(1 for ind in self.industry_keywords 
                                  if ind.lower() in industry or ind.lower() in description)
            
            if industry_matches >= 3:
                score = 3.0
            elif industry_matches >= 2:
                score = 2.5
            elif industry_matches >= 1:
                score = 2.0
            elif sector in ['Technology', 'Industrials', 'Healthcare']:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_backlog(self, info, finnhub_data):
        """Score 3: Large Backlogs (0-2)"""
        
        score = 0
        
        try:
            # Try Finnhub metrics first
            if finnhub_data and 'metrics' in finnhub_data:
                metrics = finnhub_data['metrics']
                gross_margin = metrics.get('grossMargin', 0)
                
                if gross_margin and gross_margin > 0:
                    if gross_margin > 0.45:
                        score = 2.0
                    elif gross_margin > 0.35:
                        score = 1.5
                    elif gross_margin > 0.25:
                        score = 1.0
            
            # Fallback to yfinance
            if score == 0:
                gross_profit = info.get('grossProfits', 0)
                total_revenue = info.get('totalRevenue', 0)
                
                if gross_profit and total_revenue and total_revenue > 0:
                    gross_margin = gross_profit / total_revenue
                    if gross_margin > 0.45:
                        score = 2.0
                    elif gross_margin > 0.35:
                        score = 1.5
                    elif gross_margin > 0.25:
                        score = 1.0
            
            return score
        except:
            return 0
    
    def _score_revenue_growth(self, info, finnhub_data):
        """Score 4: Revenue Growth (0-2)"""
        
        score = 0
        
        try:
            # Try Finnhub first
            if finnhub_data and 'metrics' in finnhub_data:
                metrics = finnhub_data['metrics']
                revenue_growth = metrics.get('revenueGrowth', 0)
                
                if revenue_growth and revenue_growth > 0:
                    if revenue_growth >= 0.25:
                        score = 2.0
                    elif revenue_growth >= 0.15:
                        score = 1.5
                    elif revenue_growth >= 0.05:
                        score = 1.0
            
            # Fallback to yfinance
            if score == 0:
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
        """Score 5: Profitability (0-1.5)"""
        
        score = 0
        
        try:
            # Try Finnhub first
            if finnhub_data and 'metrics' in finnhub_data:
                metrics = finnhub_data['metrics']
                net_margin = metrics.get('netMargin', 0)
                
                if net_margin and net_margin > 0:
                    if net_margin > 0.12:
                        score = 1.5
                    elif net_margin > 0.08:
                        score = 1.2
                    elif net_margin > 0.03:
                        score = 0.8
                    elif net_margin > 0:
                        score = 0.4
            
            # Fallback to yfinance
            if score == 0:
                net_income = info.get('netIncomeToCommon', 0)
                total_revenue = info.get('totalRevenue', 0)
                
                if net_income and total_revenue and total_revenue > 0:
                    net_margin = net_income / total_revenue
                    
                    if net_margin > 0.12:
                        score = 1.5
                    elif net_margin > 0.08:
                        score = 1.2
                    elif net_margin > 0.03:
                        score = 0.8
                    elif net_margin > 0:
                        score = 0.4
            
            return score
        except:
            return 0
    
    def _score_tailwind(self, symbol, info, finnhub_data):
        """Score 6: Industry Tailwinds (0-1.5)"""
        
        score = 0
        
        try:
            industry = (info.get('industry', '') or '').lower()
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            # Count tailwind keyword matches
            tailwind_matches = sum(1 for d in self.tailwind_keywords 
                                  if d.lower() in industry or d.lower() in description)
            
            if tailwind_matches >= 3:
                score = 1.5
            elif tailwind_matches >= 2:
                score = 1.2
            elif tailwind_matches >= 1:
                score = 0.8
            
            return score
        except:
            return 0
    
    def _score_execution(self, symbol):
        """Score 7: Execution Excellence (0-1.0)"""
        
        score = 0
        
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1y')
            
            if len(hist) > 0:
                start_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]
                
                if start_price > 0:
                    ytd_return = (current_price - start_price) / start_price
                    
                    if ytd_return >= 0.40:
                        score = 1.0
                    elif ytd_return >= 0.15:
                        score = 0.7
                    elif ytd_return >= 0:
                        score = 0.4
            
            return score
        except:
            return 0
    
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
        """Public method to get rating"""
        return self._get_rating(score)
