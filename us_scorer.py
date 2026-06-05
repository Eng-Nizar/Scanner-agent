"""
US Stock Scorer - 7-Reason Framework
Scores US stocks on government contracts, growth, profitability, etc.
"""

import yfinance as yf
from config import Config

class USStockScorer:
    """Score US stocks on 7-reason framework"""
    
    def __init__(self):
        self.defense_keywords = Config.US_DEFENSE_KEYWORDS
    
    def score_stock(self, symbol):
        """
        Score a US stock (0-14 scale)
        Returns dict with all scores and metrics
        """
        
        try:
            # Get stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Verify it's a US stock
            if not self._is_us_stock(info):
                return None
            
            scores = {}
            
            # Score on 7 reasons (0-2 each)
            scores['gov_contracts'] = self._score_gov_contracts(symbol, info)
            scores['national_security'] = self._score_national_security(symbol, info)
            scores['backlog'] = self._score_backlog(symbol, info)
            scores['revenue_growth'] = self._score_revenue_growth(symbol, info)
            scores['profitability'] = self._score_profitability(symbol, info)
            scores['industry_tailwinds'] = self._score_industry_tailwinds(symbol, info)
            scores['execution'] = self._score_execution(symbol, info)
            
            # Calculate totals
            total_score = sum(scores.values())
            scores['total'] = total_score
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
            scores['price_to_sales'] = self._calculate_ps_ratio(info)
            
            return scores
            
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")
            return None
    
    def _is_us_stock(self, info):
        """Verify stock is US-listed"""
        
        exchange = info.get('exchange', '').upper()
        
        # Check exchange
        if exchange not in Config.EXCHANGES:
            return False
        
        return True
    
    def _score_gov_contracts(self, symbol, info):
        """Score 1: Government Contracts & Strategic Validation (0-2)"""
        
        score = 0
        
        try:
            description = info.get('longBusinessSummary', '').lower()
            sector = info.get('sector', '').lower()
            
            # Count keyword matches
            keyword_count = sum(
                1 for keyword in self.defense_keywords 
                if keyword.lower() in description
            )
            
            if keyword_count >= 3:
                score = 2.0
            elif keyword_count >= 1:
                score = 1.0
            
            # Boost if defense sector
            if 'defense' in sector or 'aerospace' in sector:
                score = min(score + 0.5, 2.0)
            
            return score
        except:
            return 0
    
    def _score_national_security(self, symbol, info):
        """Score 2: National Security / Strategic Importance (0-2)"""
        
        score = 0
        
        try:
            industry = info.get('industry', '').lower()
            sector = info.get('sector', '').lower()
            description = info.get('longBusinessSummary', '').lower()
            
            us_defense_industries = [
                'defense', 'aerospace', 'security', 'cybersecurity',
                'drone', 'satellite', 'intelligence', 'military',
                'space technology', 'defense contractors',
                'aerospace & defense'
            ]
            
            if any(ind in industry for ind in us_defense_industries):
                score = 2.0
            elif 'defense' in description:
                score = 1.5
            elif sector in ['Technology', 'Industrials']:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_backlog(self, symbol, info):
        """Score 3: Large Backlogs = Revenue Visibility (0-2)"""
        
        score = 0
        
        try:
            gross_profit = info.get('grossProfits', 0)
            total_revenue = info.get('totalRevenue', 0)
            
            if gross_profit and total_revenue:
                gross_margin = gross_profit / total_revenue
                
                if gross_margin > 0.40:
                    score = 1.5
                elif gross_margin > 0.30:
                    score = 1.0
            
            return min(score, 2.0)
        except:
            return 0
    
    def _score_revenue_growth(self, symbol, info):
        """Score 4: Exceptional Revenue Growth (30%+ YoY) (0-2)"""
        
        score = 0
        
        try:
            revenue_growth = info.get('revenueGrowth', 0)
            
            if revenue_growth and revenue_growth >= 0.30:
                score = 2.0
            elif revenue_growth and revenue_growth >= 0.20:
                score = 1.5
            elif revenue_growth and revenue_growth >= 0.10:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_profitability(self, symbol, info):
        """Score 5: Path to / Achieving Profitability (0-2)"""
        
        score = 0
        
        try:
            net_income = info.get('netIncomeToCommon', 0)
            total_revenue = info.get('totalRevenue', 0)
            
            if net_income and total_revenue:
                net_margin = net_income / total_revenue
                
                if net_margin > 0.10:
                    score = 2.0
                elif net_margin > 0.05:
                    score = 1.5
                elif net_margin > 0:
                    score = 1.0
            
            return score
        except:
            return 0
    
    def _score_industry_tailwinds(self, symbol, info):
        """Score 6: Positioned in Booming Industries with Tailwinds (0-2)"""
        
        score = 0
        
        try:
            industry = info.get('industry', '').lower()
            description = info.get('longBusinessSummary', '').lower()
            
            booming = [
                'ai', 'artificial intelligence',
                'defense', 'cybersecurity',
                'drone', 'space', 'satellite',
                'autonomous', 'machine learning',
                'defense contractor', 'aerospace',
                'us government', 'federal'
            ]
            
            matches = sum(1 for b in booming if b in industry or b in description)
            
            if matches >= 2:
                score = 2.0
            elif matches >= 1:
                score = 1.5
            elif 'technology' in industry:
                score = 1.0
            
            return score
        except:
            return 0
    
    def _score_execution(self, symbol, info):
        """Score 7: Execution Excellence (0-2)"""
        
        score = 0
        
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1y')
            
            if len(hist) > 0:
                start_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]
                
                if start_price > 0:
                    ytd_return = (current_price - start_price) / start_price
                    
                    if ytd_return >= 0.50:
                        score = 2.0
                    elif ytd_return >= 0.20:
                        score = 1.5
                    elif ytd_return >= 0:
                        score = 1.0
            
            return score
        except:
            return 0
    
    def _calculate_ps_ratio(self, info):
        """Calculate Price-to-Sales ratio"""
        
        try:
            market_cap = info.get('marketCap', 0)
            revenue = info.get('totalRevenue', 0)
            
            if market_cap and revenue:
                return market_cap / revenue
            
            return None
        except:
            return None
    
    def _get_rating(self, score):
        """Convert score to rating"""
        
        if score >= 12:
            return "STRONG BUY 🚀"
        elif score >= 10:
            return "BUY ⭐"
        elif score >= 7:
            return "BUY 📈"
        elif score >= 5:
            return "HOLD ⏸"
        else:
            return "AVOID ❌"
