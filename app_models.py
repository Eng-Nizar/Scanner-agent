"""
Database Models for US Stock Scanner
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class USStock(db.Model):
    """US Stock Model - Optimized for Value Screening"""
    
    __tablename__ = 'us_stock'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    exchange = db.Column(db.String(10), nullable=False)
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    
    # Price & Market Cap (IMPORTANT FOR SORTING)
    current_price = db.Column(db.Float, nullable=False, index=True)
    market_cap = db.Column(db.Float, index=True)
    shares_outstanding = db.Column(db.Float)
    
    # Trading Metrics
    daily_volume = db.Column(db.Integer)
    fifty_two_week_low = db.Column(db.Float)
    fifty_two_week_high = db.Column(db.Float)
    
    # 7 REASON SCORES (0-2 each = 0-14 total)
    gov_contracts_score = db.Column(db.Float, default=0)
    national_security_score = db.Column(db.Float, default=0)
    backlog_score = db.Column(db.Float, default=0)
    revenue_growth_score = db.Column(db.Float, default=0)
    profitability_score = db.Column(db.Float, default=0)
    industry_tailwinds_score = db.Column(db.Float, default=0)
    execution_score = db.Column(db.Float, default=0)
    
    # Total Score & Rating
    total_score = db.Column(db.Float, default=0, index=True)
    rating = db.Column(db.String(20))
    
    # Financial Metrics
    revenue_ttm = db.Column(db.Float)
    revenue_growth_pct = db.Column(db.Float)
    net_income = db.Column(db.Float)
    eps = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    gross_margin = db.Column(db.Float)
    net_margin = db.Column(db.Float)
    backlog_size = db.Column(db.Float)
    backlog_growth_pct = db.Column(db.Float)
    
    # Government & Contract Info
    gov_contract_mentions = db.Column(db.Integer, default=0)
    latest_contract = db.Column(db.Text)
    latest_news = db.Column(db.Text)
    
    # Value Metrics
    price_to_book = db.Column(db.Float)
    price_to_sales = db.Column(db.Float)
    
    # Metadata
    last_scanned = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    alerts = db.relationship('USAlert', backref='stock', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<USStock {self.symbol}: ${self.current_price} - Score {self.total_score}/14>'


class USAlert(db.Model):
    """Alert for High-Quality Stocks"""
    
    __tablename__ = 'us_alert'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('us_stock.id'), nullable=False)
    
    alert_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    score_at_alert = db.Column(db.Float)
    price_at_alert = db.Column(db.Float)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<USAlert: {self.stock.symbol} - {self.alert_type}>'


class ScanRun(db.Model):
    """Track each scan execution"""
    
    __tablename__ = 'scan_run'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Statistics
    stocks_scanned = db.Column(db.Integer)
    high_score_stocks = db.Column(db.Integer)
    cheap_gems_found = db.Column(db.Integer)
    
    avg_score = db.Column(db.Float)
    top_score = db.Column(db.Float)
    
    status = db.Column(db.String(50))
    error_message = db.Column(db.Text)
    scan_duration_seconds = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<ScanRun {self.scan_date}>'
