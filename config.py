"""
Configuration for US Stock Scanner
US Market Only - 3,000+ stocks
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Production configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///us_stocks.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Scanner Settings
    SCAN_INTERVAL_HOURS = 12  # Run every 12 hours
    
    # US MARKET ONLY
    MARKET = 'US'
    EXCHANGES = ['NASDAQ', 'NYSE', 'AMEX']
    MIN_PRICE = 0.50
    MAX_PRICE = None
    MIN_VOLUME = 100000
    
    # Score Thresholds
    SCORE_THRESHOLD_ALERT = 5  # Alert if score >= 5
    CHEAP_PRICE_THRESHOLD = 20  # "Cheap" stocks under $20
    
    # Price Brackets
    PRICE_BRACKETS = {
        'ultra_cheap': (0.50, 5.00),
        'cheap': (5.00, 20.00),
        'moderate': (20.00, 50.00),
        'expensive': (50.00, 100.00),
        'premium': (100.00, float('inf'))
    }
    
    # Market Cap Brackets
    MARKET_CAP_BRACKETS = {
        'micro': (0, 50_000_000),
        'small': (50_000_000, 300_000_000),
        'mid': (300_000_000, 2_000_000_000),
        'large': (2_000_000_000, float('inf'))
    }
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    FINNHUB_KEY = os.getenv('FINNHUB_KEY', '')
    
    # US Defense Keywords
    US_DEFENSE_KEYWORDS = [
        'Department of Defense',
        'DOD', 'Pentagon',
        'Space Force', 'Air Force', 'Naval',
        'DARPA', 'NSA', 'CIA',
        'government contract',
        'federal contract',
        'military',
        'defense',
        'national security',
        'hypersonic',
        'drone',
        'autonomous',
        'cybersecurity',
        'AI defense',
        'intelligence',
        'US Army', 'US Navy', 'US Marine',
        'US government',
        'Congress', 'Senate',
        'aerospace',
        'space technology',
        'satellite',
        'security',
        'weapons',
        'missile'
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
