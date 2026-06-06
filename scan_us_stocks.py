#!/usr/bin/env python
"""
US Stock Scanner - Main scanning script
Scans US stocks and saves results to database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from app_models import USStock, USAlert, ScanRun
from us_scorer import USStockScorer
from config import Config
import yfinance as yf
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockScanner:
    def __init__(self):
        self.scorer = USStockScorer()
        self.stocks_processed = 0
        self.high_score_stocks = 0
        self.cheap_gems = 0
        
    def get_stock_list(self):
        """Get list of popular US stocks to scan"""
        stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B', 'JNJ', 'V',
            'WMT', 'PG', 'XOM', 'MA', 'HD', 'COST', 'MCD', 'ABBV', 'LLY', 'KO',
            'PEP', 'AVGO', 'CRM', 'AMD', 'NFLX', 'ACN', 'TXN', 'QCOM', 'MU', 'IBM',
            'INTC', 'CSCO', 'ORCL', 'ADBE', 'GILD', 'AMAT', 'CRWD', 'SNOW', 'NOW', 'PANW',
            'NET', 'DDOG', 'MDB', 'COIN', 'RBLX', 'DASH', 'UPST', 'U', 'RIOT', 'MSTR',
            'KTOS', 'TENB', 'BBAI', 'RKLB', 'ELDN', 'LCID', 'PLTR', 'F', 'GM', 'RIVN',
            'PCAR', 'DE', 'CAT', 'MMM', 'BA', 'RTX', 'LMT', 'GD', 'NOC', 'HII',
            'LDOS', 'AVAV', 'LHX', 'VSAT', 'MAXR', 'AERI', 'SAIC', 'CACI', 'EACL', 'MARA'
        ]
        return stocks
    
    def scan_single_stock(self, symbol):
        """Scan a single stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'currentPrice' not in info:
                return None
            
            stock = USStock.query.filter_by(symbol=symbol).first()
            if not stock:
                stock = USStock(
                    symbol=symbol,
                    company_name=info.get('longName', symbol),
                    exchange=info.get('exchange', 'NASDAQ'),
                    current_price=0
                )
                db.session.add(stock)
            
            stock.current_price = info.get('currentPrice', 0) or info.get('bid', 0) or 0
            stock.company_name = info.get('longName', symbol)
            stock.exchange = info.get('exchange', 'NASDAQ')
            stock.sector = info.get('sector', '')
            stock.industry = info.get('industry', '')
            stock.market_cap = info.get('marketCap', 0)
            stock.pe_ratio = info.get('trailingPE', 0)
            stock.gross_margin = info.get('grossMargins', 0)
            stock.net_margin = info.get('profitMargins', 0)
            stock.revenue_ttm = info.get('totalRevenue', 0)
            stock.fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
            stock.fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)
            
            scores = self.scorer.score_stock(symbol, info)
            stock.total_score = scores.get('total_score', 0)
            stock.rating = self.scorer.get_rating(stock.total_score)
            stock.gov_contracts_score = scores.get('gov_contracts_score', 0)
            stock.national_security_score = scores.get('national_security_score', 0)
            stock.revenue_growth_score = scores.get('revenue_growth_score', 0)
            stock.profitability_score = scores.get('profitability_score', 0)
            stock.last_scanned = datetime.utcnow()
            
            db.session.commit()
            
            if stock.total_score >= 10:
                self.high_score_stocks += 1
            if stock.current_price < 20 and stock.total_score >= 7:
                self.cheap_gems += 1
            
            logger.info(f"✓ {symbol:6} - Score: {stock.total_score:5.1f}/14 - ${stock.current_price:8.2f} - {stock.rating}")
            return stock
            
        except Exception as e:
            logger.warning(f"✗ {symbol}: {str(e)[:50]}")
            return None
    
    def run_scan(self):
        """Run the full stock scan"""
        logger.info("=" * 70)
        logger.info("🚀 STARTING US STOCK SCANNER")
        logger.info("=" * 70)
        
        with app.app_context():
            scan_run = ScanRun(status='running')
            db.session.add(scan_run)
            db.session.commit()
            
            start_time = datetime.utcnow()
            
            stocks = self.get_stock_list()
            logger.info(f"\n📊 Scanning {len(stocks)} stocks...")
            logger.info("=" * 70)
            
            for symbol in stocks:
                self.scan_single_stock(symbol)
                self.stocks_processed += 1
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            scan_run.stocks_scanned = self.stocks_processed
            scan_run.high_score_stocks = self.high_score_stocks
            scan_run.cheap_gems_found = self.cheap_gems
            scan_run.status = 'completed'
            scan_run.scan_duration_seconds = int(duration)
            
            avg_score = db.session.query(db.func.avg(USStock.total_score)).scalar() or 0
            top_score = db.session.query(db.func.max(USStock.total_score)).scalar() or 0
            
            scan_run.avg_score = round(avg_score, 2)
            scan_run.top_score = round(top_score, 2)
            
            db.session.commit()
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ SCAN COMPLETE!")
            logger.info("=" * 70)
            logger.info(f"📈 Stocks scanned:      {self.stocks_processed}")
            logger.info(f"⭐ High-score (≥10):    {self.high_score_stocks}")
            logger.info(f"💎 Cheap gems (<$20):   {self.cheap_gems}")
            logger.info(f"📊 Average score:       {avg_score:.2f}/14")
            logger.info(f"🏆 Top score:           {top_score:.1f}/14")
            logger.info(f"⏱️  Duration:            {duration:.0f} seconds")
            logger.info("=" * 70)
            logger.info("\n✨ Dashboard updated! Visit your Scanner-agent URL to see results!")

if __name__ == '__main__':
    scanner = StockScanner()
    scanner.run_scan()
