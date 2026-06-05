"""
Flask Routes for US Stock Scanner Dashboard
"""

from flask import Blueprint, render_template, jsonify, request
from app.models import USStock, USAlert, ScanRun, db
from sqlalchemy import desc
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def us_dashboard():
    """
    Main Dashboard - US Stocks Only
    Shows: Most matched stocks + Cheap gems
    """
    
    # Get top scored stocks (any price)
    top_matched = USStock.query.order_by(
        desc(USStock.total_score)
    ).limit(30).all()
    
    # Get cheap high-quality stocks (< $20, score >= 7)
    cheap_gems = USStock.query.filter(
        USStock.current_price < Config.CHEAP_PRICE_THRESHOLD,
        USStock.total_score >= 7
    ).order_by(USStock.current_price).limit(30).all()
    
    # Get latest scan
    latest_scan = ScanRun.query.order_by(
        desc(ScanRun.scan_date)
    ).first()
    
    return render_template(
        'us_dashboard.html',
        top_matched=top_matched,
        cheap_gems=cheap_gems,
        latest_scan=latest_scan
    )


@main_bp.route('/stock/<symbol>')
def stock_detail(symbol):
    """
    Stock Detail Page
    """
    
    stock = USStock.query.filter_by(symbol=symbol).first()
    
    if not stock:
        return "Stock not found", 404
    
    alerts = USAlert.query.filter_by(stock_id=stock.id).order_by(
        desc(USAlert.triggered_at)
    ).limit(10).all()
    
    return render_template(
        'stock_detail.html',
        stock=stock,
        alerts=alerts
    )


@main_bp.route('/api/stocks')
def get_stocks_api():
    """
    API Endpoint - Get stocks data
    Parameters:
    - filter: 'all', 'high_score', 'cheap', 'ultra_cheap'
    - sort: 'score', 'price', 'market_cap'
    - limit: number of stocks to return
    """
    
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'score')
    limit = int(request.args.get('limit', 100))
    
    query = USStock.query
    
    # Apply filters
    if filter_type == 'high_score':
        query = query.filter(USStock.total_score >= 10)
    elif filter_type == 'cheap':
        query = query.filter(
            USStock.current_price < 20,
            USStock.total_score >= 7
        )
    elif filter_type == 'ultra_cheap':
        query = query.filter(
            USStock.current_price < 10,
            USStock.total_score >= 5
        )
    
    # Apply sorting
    if sort_by == 'score':
        query = query.order_by(desc(USStock.total_score))
    elif sort_by == 'price':
        query = query.order_by(USStock.current_price)
    elif sort_by == 'market_cap':
        query = query.order_by(desc(USStock.market_cap))
    
    stocks = query.limit(limit).all()
    
    return jsonify([{
        'symbol': s.symbol,
        'name': s.company_name,
        'price': s.current_price,
        'market_cap': s.market_cap,
        'score': s.total_score,
        'rating': s.rating,
        'gov_contracts': s.gov_contracts_score,
        'revenue_growth': s.revenue_growth_score,
        'pe_ratio': s.pe_ratio,
        'exchange': s.exchange
    } for s in stocks])


@main_bp.route('/api/scan-history')
def scan_history_api():
    """
    API Endpoint - Scan history
    """
    
    history = ScanRun.query.order_by(
        desc(ScanRun.scan_date)
    ).limit(30).all()
    
    return jsonify([{
        'date': h.scan_date.isoformat(),
        'scanned': h.stocks_scanned,
        'high_score': h.high_score_stocks,
        'cheap_gems': h.cheap_gems_found,
        'avg_score': h.avg_score,
        'top_score': h.top_score,
        'status': h.status,
        'duration': h.scan_duration_seconds
    } for h in history])


@main_bp.route('/api/stats')
def get_stats_api():
    """
    API Endpoint - Current statistics
    """
    
    total_stocks = USStock.query.count()
    high_score = USStock.query.filter(USStock.total_score >= 5).count()
    cheap_gems = USStock.query.filter(
        USStock.current_price < 20,
        USStock.total_score >= 7
    ).count()
    
    avg_score = db.session.query(
        db.func.avg(USStock.total_score)
    ).scalar() or 0
    
    latest_scan = ScanRun.query.order_by(
        desc(ScanRun.scan_date)
    ).first()
    
    return jsonify({
        'total_stocks': total_stocks,
        'high_score_stocks': high_score,
        'cheap_gems': cheap_gems,
        'avg_score': round(avg_score, 2),
        'last_scan': latest_scan.scan_date.isoformat() if latest_scan else None,
        'market': 'US',
        'exchanges': ', '.join(Config.EXCHANGES)
    })


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'US Stock Scanner'})


@main_bp.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'error': 'Not found'}), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
