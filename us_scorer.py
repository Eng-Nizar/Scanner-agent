"""
US Stock Scorer - Hybrid Approach
Uses Finnhub for detailed data, falls back to yfinance + defense keywords
Designed to work reliably with available data
"""

import yfinance as yf
import requests
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

class USStockScorer:
    """Score US stocks - Hybrid Finnhub + yfinance approach"""
    
    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_KEY', '')
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.defense_keywords = Config.US_DEFENSE_KEYWORDS
    
    def score_stock(self, symbol):
        """
        Score a US stock (0-14 scale)
        Uses: Finnhub data + yfinance + defense keywords
        """
        
        try:
            # Get basic price info from yfinance (ALWAYS works)
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'currentPrice' not in info:
                return None
            
            # Try to get Finnhub data (may fail, but OK if it does)
            finnhub_data = self._get_finnhub_data(symbol)
            
            scores = {}
            
            # Score on 7 reasons with DEFENSE OPTIMIZATION
            # These are DESIGNED to work even with limited data
            scores['gov_contracts'] = self._score_gov_contracts(symbol, info, finnhub_data)
            scores['national_security'] = self._score_national_security(symbol, info, finnhub_data)
            scores['backlog'] = self._score_backlog(info, finnhub_data)
            scores['revenue_growth'] = self._score_revenue_growth(info, finnhub_data)
            scores['profitability'] = self._score_profitability(info, finnhub_data)
            scores['industry_tailwinds'] = self._score_industry_tailwinds(symbol, info, finnhub_data)
            scores['execution'] = self._score_execution(symbol, info)
            
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
            print(f"Error scoring {symbol}: {e}")
            return None
    
    def _get_finnhub_data(self, symbol):
        """Try to get Finnhub data, but don't fail if it doesn't work"""
        
        try:
            if not self.finnhub_key:
                return {}
            
            # Get profile
            url = f"{self.finnhub_base}/stock/profile2"
            params = {'symbol': symbol, 'token': self.finnhub_key}
            resp = requests.get(url, params=params, timeout=3)
            
            if resp.status_code == 200 and resp.json():
                profile = resp.json()
            else:
                profile = {}
            
            # Get metrics
            url = f"{self.finnhub_base}/stock/metric"
            params = {'symbol': symbol, 'metric': 'all', 'token': self.finnhub_key}
            resp = requests.get(url, params=params, timeout=3)
            
            if resp.status_code == 200 and resp.json():
                metrics = resp.json().get('metric', {})
            else:
                metrics = {}
            
            return {'profile': profile, 'metrics': metrics}
        
        except Exception as e:
            # Silently return empty - we can score without Finnhub
            return {}
    
    def _score_gov_contracts(self, symbol, info, finnhub_data):
        """Score 1: Government Contracts (0-3) - PRIMARY SCORING"""
        
        score = 0
        
        try:
            # Get description from both sources
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            if finnhub_data and 'profile' in finnhub_data:
                profile = finnhub_data['profile']
                description += ' ' + (profile.get('description', '') or '').lower()
            
            name = (info.get('longName', '') or '').lower()
            
            # DEFENSE KEYWORDS - Most important!
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
            sector = (info.get('sector', '') or '').lower()
            if 'defense' in sector or 'aerospace' in sector:
                score = min(score + 0.5, 3.0)
            
            return score
        except:
            return 0
    
    def _score_national_security(self, symbol, info, finnhub_data):
        """Score 2: National Security (0-3)"""
        
        score = 0
        
        try:
            industry = (info.get('industry', '') or '').lower()
            sector = (info.get('sector', '') or '').lower()
            description = (info.get('longBusinessSummary', '') or '').lower()
            
            defense_industries = [
                'defense', 'aerospace', 'security', 'cybersecurity',
                'drone', 'satellite', 'intelligence', 'military',
                'space technology', 'defense contractors', 'aerospace & defense',
                'guided missiles', 'aircraft', 'weapons systems'
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
            
            # Fallback to yfinance if no Finnhub data
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
    
    def _score_industry_tailwinds(self, symbol, info, finnhub_data):
        """Score 6: Industry Tailwinds (0-1.5)"""
        
        score = 0
        
        try:
            industry = (info.get('industry', '') or '').lower()
            description = (info.get('longBusinessSummary', '') or '').lower()
            
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
    
    def _score_execution(self, symbol, info):
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
