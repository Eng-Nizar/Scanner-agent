"""
US Stock Scorer - Finnhub Integration
Scores US stocks using Finnhub API for real financial data
Defense-focused: Government contracts, national security
"""

import requests
import yfinance as yf
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

class USStockScorer:
    """Score US stocks using Finnhub API for fundamentals"""
    
    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_KEY', '')
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.defense_keywords = Config.US_DEFENSE_KEYWORDS
        
        if not self.finnhub_key:
            print("⚠️  WARNING: FINNHUB_KEY not found in environment")
    
    def score_stock(self, symbol):
        """
        Score a US stock using Finnhub data (0-14 scale)
        Returns dict with all scores and metrics
        """
        
        try:
            # Get company profile from Finnhub
            profile = self._get_company_profile(symbol)
            if not profile:
                return None
            
            # Get financial metrics from Finnhub
            metrics = self._get_financial_metrics(symbol)
            
            # Get current price from yfinance (fast & reliable)
            price_info = self._get_price_info(symbol)
            if not price_info:
                return None
            
            scores = {}
            
            # Score on 7 reasons with DEFENSE OPTIMIZATION
            scores['gov_contracts'] = self._score_gov_contracts(symbol, profile)
            scores['national_security'] = self._score_national_security(symbol, profile)
            scores['backlog'] = self._score_backlog(metrics, profile)
            scores['revenue_growth'] = self._score_revenue_growth(metrics)
            scores['profitability'] = self._score_profitability(metrics)
            scores['industry_tailwinds'] = self._score_industry_tailwinds(symbol, profile)
            scores['execution'] = self._score_execution(symbol)
            
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
            scores['current_price'] = price_info.get('current_price', 0)
            scores['market_cap'] = price_info.get('market_cap', 0)
            scores['pe_ratio'] = metrics.get('pe', 0) if metrics else 0
            scores['price_to_sales'] = metrics.get('ps', 0) if metrics else 0
            
            return scores
            
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")
            return None
    
    def _get_company_profile(self, symbol):
        """Get company profile from Finnhub"""
        
        try:
            url = f"{self.finnhub_base}/stock/profile2"
            params = {'symbol': symbol, 'token': self.finnhub_key}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data
            
            return None
        except Exception as e:
            print(f"Error getting profile for {symbol}: {e}")
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
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'metric' in data:
                    return data['metric']
            
            return None
        except Exception as e:
            print(f"Error getting metrics for {symbol}: {e}")
            return None
    
    def _get_price_info(self, symbol):
        """Get price info from yfinance"""
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'exchange': info.get('exchange', '')
            }
        except:
            return None
    
    def _score_gov_contracts(self, symbol, profile):
        """Score 1: Government Contracts & Strategic Validation (0-3)"""
        
        score = 0
        
        try:
            description = (profile.get('description', '') or '').lower()
            name = (profile.get('name', '') or '').lower()
            
            # ENHANCED: Defense keyword matching
            gov_keywords = [
                'pentagon', 'dod', 'nasa', 'government', 'defense',
                'military', 'contract', 'federal', 'classified',
                'aerospace', 'defense contractor', 'weapons',
                'u.s. government', 'us government', 'armed forces'
            ]
            
            keyword_count = sum(1 for kw in gov_keywords if kw in description or kw in name)
            
            if keyword_count >= 4:
                score = 3.0
            elif keyword_count >= 2:
                score = 2.5
            elif keyword_count >= 1:
                score = 1.5
            else:
                score = 0.5
            
            # Boost if defense/aerospace sector
            sector = (profile.get('sector', '') or '').lower()
            if 'defense' in sector or 'aerospace' in sector:
                score = min(score + 0.5, 3.0)
            
            return score
        except:
            return 0
    
    def _score_national_security(self, symbol, profile):
        """Score 2: National Security / Strategic Importance (0-3)"""
        
        score = 0
        
        try:
            industry = (profile.get('industry', '') or '').lower()
            sector = (profile.get('sector', '') or '').lower()
            description = (profile.get('description', '') or '').lower()
            
            # CRITICAL defense industries
            defense_industries = [
                'defense', 'aerospace', 'security', 'cybersecurity',
                'drone', 'satellite', 'intelligence', 'military',
                'space technology', 'defense contractors', 'aerospace & defense',
                'guided missiles', 'aircraft', 'weapons systems',
                'space exploration'
            ]
            
            if any(ind in industry for ind in defense_industries):
                score = 3.0
            elif 'defense' in description and 'government' in description:
                score = 2.5
            elif 'defense' in description:
                score = 2.0
            elif 'cyber' in industry and 'security' in industry:
                score = 2.0
            elif sector in ['Technology', 'Industrials']:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_backlog(self, metrics, profile):
        """Score 3: Large Backlogs = Revenue Visibility (0-2)"""
        
        score = 0
        
        try:
            if not metrics:
                return 0
            
            # Get gross margin from Finnhub metrics
            gross_margin = metrics.get('grossMargin', 0)
            
            if gross_margin and gross_margin > 0:
                if gross_margin > 0.45:
                    score = 2.0
                elif gross_margin > 0.35:
                    score = 1.5
                elif gross_margin > 0.25:
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _score_revenue_growth(self, metrics):
        """Score 4: Revenue Growth (0-2)"""
        
        score = 0
        
        try:
            if not metrics:
                return 0
            
            # Get revenue growth from Finnhub
            revenue_growth = metrics.get('revenueGrowth', 0)
            
            if revenue_growth and revenue_growth > 0:
                if revenue_growth >= 0.25:
                    score = 2.0
                elif revenue_growth >= 0.15:
                    score = 1.5
                elif revenue_growth >= 0.05:
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _score_profitability(self, metrics):
        """Score 5: Path to / Achieving Profitability (0-1.5)"""
        
        score = 0
        
        try:
            if not metrics:
                return 0
            
            # Get net margin from Finnhub
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
            
            return score
        except:
            return 0
    
    def _score_industry_tailwinds(self, symbol, profile):
        """Score 6: Industry Tailwinds (0-1.5)"""
        
        score = 0
        
        try:
            industry = (profile.get('industry', '') or '').lower()
            description = (profile.get('description', '') or '').lower()
            
            # DEFENSE TAILWINDS
            defense_tailwinds = [
                'ai', 'artificial intelligence', 'machine learning',
                'defense', 'cybersecurity', 'cyber threat',
                'drone', 'space', 'satellite', 'autonomous',
                'defense contractor', 'aerospace', 'pentagon',
                'armed forces', 'intelligence', 'military tech'
            ]
            
            matches = sum(1 for d in defense_tailwinds if d in industry or d in description)
            
            if matches >= 3:
                score = 1.5
            elif matches >= 2:
                score = 1.2
            elif matches >= 1:
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
            return "🚀 STRONG BUY - DEFENSE LEADER"
        elif score >= 10:
            return "⭐ BUY - GOVT CONTRACTOR"
        elif score >= 8:
            return "📈 BUY - DEFENSE PLAY"
        elif score >= 6:
            return "⏸ HOLD - MONITOR"
        elif score >= 4:
            return "👀 WATCH - POTENTIAL"
        else:
            return "❌ AVOID - LOW SCORE"
    
    def get_rating(self, score):
        """Public method to get rating"""
        return self._get_rating(score)
