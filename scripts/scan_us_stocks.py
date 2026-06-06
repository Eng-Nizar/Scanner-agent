mkdir -p scripts
cat > scripts/scan_us_stocks.py << 'EOF'
import sys
sys.path.insert(0, '/app')

from app_models import db, USStock, USAlert, ScanRun
from config import Config
from us_scorer import USStockScorer
import yfinance as yf
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_stocks():
    """Main scan function"""
    from main import app
    
    with app.app_context():
        logger.info("🚀 Starting US Stock Scanner...")
        
        # Get list of stocks to scan (NASDAQ + NYSE)
        try:
            # Quick test with top 50 stocks
            stocks_to_scan = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B', 'JNJ', 'V',
                            'WMT', 'PG', 'XOM', 'MA', 'HD', 'COST', 'MCD', 'ABBV', 'LLY', 'KO',
                            'PEP', 'AVGO', 'CRM', 'AMD', 'NFLX', 'ACN', 'TXN', 'QCOM', 'MU', 'IBM',
                            'INTC', 'CSCO', 'ORCL', 'ADBE', 'AMZN', 'GILD', 'AMAT', 'CRWD', 'SNOW', 'NOW',
                            'PANW', 'NET', 'DDOG', 'MDB', 'RBLX', 'U', 'DASH', 'UPST', 'COIN', 'RIOT']
            
            logger.info(f"📊 Scanning {len(stocks_to_scan)} stocks...")
            
            scorer = USStockScorer()
            scan_run = ScanRun(status='running', stocks_scanned=len(stocks_to_scan))
            db.session.add(scan_run)
            db.session.commit()
            
            high_score_count = 0
            cheap_gems_count = 0
            
            for symbol in stocks_to_scan:
                try:
                    stock = USStock.query.filter_by(symbol=symbol).first()
                    if not stock:
                        stock = USStock(symbol=symbol, company_name=symbol, exchange='NASDAQ', current_price=0)
                        db.session.add(stock)
                    
                    # Fetch data
                    data = yf.Ticker(symbol)
                    info = data.info
                    
                    stock.current_price = info.get('currentPrice', 0) or info.get('bid', 0) or 0
                    stock.company_name = info.get('longName', symbol)
                    stock.market_cap = info.get('marketCap', 0)
                    stock.pe_ratio = info.get('trailingPE', 0)
                    
                    # Score it
                    score = scorer.score_stock(symbol, info)
                    stock.total_score = score
                    stock.rating = scorer.get_rating(score)
                    stock.last_scanned = datetime.utcnow()
                    
                    if score >= 10:
                        high_score_count += 1
                    if stock.current_price < 20 and score >= 7:
                        cheap_gems_count += 1
                    
                    db.session.commit()
                    logger.info(f"✓ {symbol}: Score {score:.1f}/14 - Rating {stock.rating}")
                    
                except Exception as e:
                    logger.warning(f"✗ {symbol}: {str(e)}")
                    continue
            
            # Update scan run
            scan_run.status = 'completed'
            scan_run.high_score_stocks = high_score_count
            scan_run.cheap_gems_found = cheap_gems_count
            db.session.commit()
            
            logger.info(f"\n✅ Scan Complete!")
            logger.info(f"High-score stocks: {high_score_count}")
            logger.info(f"Cheap gems: {cheap_gems_count}")
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {str(e)}")
            scan_run.status = 'failed'
            scan_run.error_message = str(e)
            db.session.commit()

if __name__ == '__main__':
    scan_stocks()
EOF
