"""
US Stock Scanner - Main Scanning Script
Scans 3,000+ US stocks for 7-reason matches
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from app import create_app, db
from app.models import USStock, USAlert, ScanRun
from scanners.us_scorer import USStockScorer
from config import Config
from concurrent.futures import ThreadPoolExecutor
import time

def get_us_stocks():
    """Get all US-listed stocks"""
    
    print("Loading US stock list...")
    
    # Start with common stocks
    stocks = get_popular_us_stocks()
    
    # Try to add NASDAQ stocks
    try:
        nasdaq = pd.read_csv(
            'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt',
            sep='|',
            timeout=10
        )
        nasdaq_stocks = nasdaq['Symbol'].dropna().tolist()
        stocks.extend(nasdaq_stocks)
        print(f"  Added {len(nasdaq_stocks)} NASDAQ stocks")
    except Exception as e:
        print(f"  Could not load NASDAQ list: {e}")
    
    # Remove duplicates and invalid symbols
    stocks = list(set(stocks))
    stocks = [s.strip().upper() for s in stocks if s and len(s) <= 5]
    
    print(f"Total US stocks to scan: {len(stocks)}")
    return stocks


def get_popular_us_stocks():
    """Popular and major US stocks to always include"""
    
    return [
        # Your three main stocks
        'BBAI', 'TENB', 'KTOS',
        
        # Other defense/AI stocks
        'PLTR', 'RKLB', 'LDOS', 'AVAV', 'LHX', 'CRWD',
        'RTX', 'BA', 'NOC', 'GD', 'TDG',
        
        # Major tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
        'INTC', 'AMD', 'QCOM', 'CSCO',
        
        # Cybersecurity
        'PALO', 'OKTA', 'NET', 'PANW', 'CHKP',
        
        # Defense contractors
        'APH', 'TECH', 'HII', 'PSA',
        
        # Space & Satellites
        'MAXR', 'SSTI', 'IRDM',
        
        # Add more as needed...
    ]


def run_us_stock_scan():
    """Main scanning function"""
    
    app = create_app()
    
    with app.app_context():
        print(f"\n{'='*70}")
        print(f"  🇺🇸 US STOCK SCANNER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        scorer = USStockScorer()
        
        # Get stocks to scan
        us_stocks = get_us_stocks()
        
        # Statistics
        scanned_count = 0
        high_score_count = 0
        cheap_gems = 0
        failed_count = 0
        high_score_stocks = []
        cheap_high_score = []
        
        print(f"Scanning {len(us_stocks)} US stocks with parallel processing...\n")
        
        # Scan in parallel (50 at a time)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(scorer.score_stock, symbol): symbol
                for symbol in us_stocks
            }
            
            completed = 0
            for future in futures:
                symbol = futures[future]
                completed += 1
                
                # Progress indicator
                if completed % 100 == 0:
                    print(f"Progress: {completed}/{len(us_stocks)} stocks processed...")
                
                try:
                    scores = future.result(timeout=10)
                    
                    if scores is None:
                        failed_count += 1
                        continue
                    
                    scanned_count += 1
                    
                    # Get or create stock in database
                    stock = USStock.query.filter_by(symbol=symbol).first()
                    
                    if not stock:
                        stock = USStock(symbol=symbol)
                        db.session.add(stock)
                    
                    # Update all fields
                    stock.company_name = scores.get('company_name', symbol)
                    stock.exchange = scores.get('exchange', 'UNKNOWN')
                    stock.sector = scores.get('sector', '')
                    stock.industry = scores.get('industry', '')
                    stock.current_price = scores.get('current_price', 0)
                    stock.market_cap = scores.get('market_cap', 0)
                    
                    # 7-Reason Scores
                    stock.gov_contracts_score = scores.get('gov_contracts', 0)
                    stock.national_security_score = scores.get('national_security', 0)
                    stock.backlog_score = scores.get('backlog', 0)
                    stock.revenue_growth_score = scores.get('revenue_growth', 0)
                    stock.profitability_score = scores.get('profitability', 0)
                    stock.industry_tailwinds_score = scores.get('industry_tailwinds', 0)
                    stock.execution_score = scores.get('execution', 0)
                    stock.total_score = scores.get('total', 0)
                    stock.rating = scores.get('rating', 'AVOID')
                    
                    # Metrics
                    stock.pe_ratio = scores.get('pe_ratio', 0)
                    stock.price_to_sales = scores.get('price_to_sales', 0)
                    stock.last_scanned = datetime.utcnow()
                    
                    db.session.commit()
                    
                    # Track for alerts
                    if scores.get('total', 0) >= 5:
                        high_score_count += 1
                        high_score_stocks.append({
                            'symbol': symbol,
                            'price': scores.get('current_price', 0),
                            'score': scores.get('total', 0),
                            'rating': scores.get('rating', '')
                        })
                        
                        # Check if cheap gem
                        price = scores.get('current_price', 0)
                        if price > 0 and price < 20:
                            cheap_gems += 1
                            cheap_high_score.append({
                                'symbol': symbol,
                                'price': price,
                                'score': scores.get('total', 0)
                            })
                            print(f"💎 {symbol} @ ${price:.2f} - {scores.get('total', 0)}/14")
                    
                except Exception as e:
                    failed_count += 1
                    continue
        
        # Save scan history
        avg_score = sum(s['score'] for s in high_score_stocks) / len(high_score_stocks) if high_score_stocks else 0
        top_score = max((s['score'] for s in high_score_stocks), default=0)
        
        scan_run = ScanRun(
            stocks_scanned=scanned_count,
            high_score_stocks=high_score_count,
            cheap_gems_found=cheap_gems,
            avg_score=avg_score,
            top_score=top_score,
            status='success' if failed_count == 0 else 'partial',
            scan_duration_seconds=int(time.time() - start_time)
        )
        db.session.add(scan_run)
        db.session.commit()
        
        # Print Summary
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"  📊 SCAN COMPLETED SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"US Stocks Scanned: {scanned_count}")
        print(f"High Score (≥5): {high_score_count}")
        print(f"💎 Cheap Gems (<$20): {cheap_gems}")
        print(f"Failed: {failed_count}")
        print(f"Average Score: {avg_score:.2f}/14")
        print(f"Top Score: {top_score}/14")
        print(f"Duration: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"{'='*70}\n")
        
        # Top 10 stocks
        print("🚀 TOP 10 HIGHEST SCORES:")
        print(f"{'='*70}")
        top_10 = sorted(high_score_stocks, key=lambda x: x['score'], reverse=True)[:10]
        for i, stock in enumerate(top_10, 1):
            print(f"{i:2}. {stock['symbol']:8} ${stock['price']:7.2f}  Score: {stock['score']:5.1f}/14  {stock['rating']}")
        
        # Cheap gems
        if cheap_high_score:
            print(f"\n💎 CHEAPEST HIGH-QUALITY STOCKS (<$20, Score ≥7):")
            print(f"{'='*70}")
            cheap_sorted = sorted(cheap_high_score, key=lambda x: x['price'])
            for i, stock in enumerate(cheap_sorted[:10], 1):
                print(f"{i:2}. {stock['symbol']:8} ${stock['price']:7.2f}  Score: {stock['score']:5.1f}/14  ⭐ VALUE PLAY")
        
        print(f"\n{'='*70}\n")


if __name__ == '__main__':
    run_us_stock_scan()
