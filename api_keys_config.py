"""
API Keys Configuration & Validation
Configure your API keys for enhanced data access
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class APIKeysConfig:
    """Manage API keys for stock data"""
    
    # Get API keys from environment variables
    ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', '')
    FINNHUB_KEY = os.environ.get('FINNHUB_KEY', '')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    IEX_CLOUD_KEY = os.environ.get('IEX_CLOUD_KEY', '')
    
    # API Endpoints
    APIS = {
        'alpha_vantage': {
            'name': 'Alpha Vantage',
            'endpoint': 'https://www.alphavantage.co/query',
            'key': ALPHA_VANTAGE_KEY,
            'description': 'Company fundamentals (earnings, cash flow, margins)',
            'free_tier': '5 calls/min',
            'importance': 'HIGH'
        },
        'finnhub': {
            'name': 'Finnhub',
            'endpoint': 'https://finnhub.io/api/v1',
            'key': FINNHUB_KEY,
            'description': 'Government contracts, company news, estimates',
            'free_tier': '60 calls/min',
            'importance': 'HIGH'
        },
        'newsapi': {
            'name': 'NewsAPI',
            'endpoint': 'https://newsapi.org/v2',
            'key': NEWS_API_KEY,
            'description': 'Stock news and sentiment',
            'free_tier': '100 calls/day',
            'importance': 'MEDIUM'
        },
        'iex_cloud': {
            'name': 'IEX Cloud',
            'endpoint': 'https://cloud.iexapis.com/v1',
            'key': IEX_CLOUD_KEY,
            'description': 'Real-time quotes and fundamentals',
            'free_tier': '100/month',
            'importance': 'MEDIUM'
        }
    }
    
    @classmethod
    def validate_keys(cls):
        """Validate all configured API keys"""
        
        results = {}
        
        print("\n" + "="*70)
        print("🔑 API KEY VALIDATION")
        print("="*70 + "\n")
        
        for api_name, api_config in cls.APIS.items():
            key = api_config['key']
            
            print(f"📊 {api_config['name']}")
            print(f"   └─ Status: ", end='')
            
            if not key:
                print("❌ NOT CONFIGURED")
                results[api_name] = {
                    'status': 'missing',
                    'message': 'API key not found in environment'
                }
            else:
                try:
                    is_valid = cls._test_api(api_name, key)
                    if is_valid:
                        print("✅ WORKING")
                        results[api_name] = {
                            'status': 'working',
                            'message': 'API key validated successfully'
                        }
                    else:
                        print("⚠️ INVALID KEY")
                        results[api_name] = {
                            'status': 'invalid',
                            'message': 'API key test failed'
                        }
                except Exception as e:
                    print(f"⚠️ ERROR: {str(e)[:40]}")
                    results[api_name] = {
                        'status': 'error',
                        'message': str(e)
                    }
            
            print(f"   └─ Tier: {api_config['free_tier']}")
            print(f"   └─ Use: {api_config['description']}\n")
        
        return results
    
    @classmethod
    def _test_api(cls, api_name, key):
        """Test if API key is valid"""
        
        try:
            if api_name == 'alpha_vantage':
                url = f"{cls.APIS[api_name]['endpoint']}?function=OVERVIEW&symbol=AAPL&apikey={key}"
                resp = requests.get(url, timeout=5)
                return 'Error' not in resp.text and resp.status_code == 200
            
            elif api_name == 'finnhub':
                url = f"{cls.APIS[api_name]['endpoint']}/quote?symbol=AAPL&token={key}"
                resp = requests.get(url, timeout=5)
                return resp.status_code == 200 and 'c' in resp.json()
            
            elif api_name == 'newsapi':
                url = f"{cls.APIS[api_name]['endpoint']}/everything?q=stock&apiKey={key}"
                resp = requests.get(url, timeout=5)
                return resp.status_code == 200 and 'articles' in resp.json()
            
            elif api_name == 'iex_cloud':
                url = f"{cls.APIS[api_name]['endpoint']}/stable/stock/AAPL/quote?token={key}"
                resp = requests.get(url, timeout=5)
                return resp.status_code == 200
            
            return False
        except:
            return False
    
    @classmethod
    def get_setup_instructions(cls):
        """Get instructions for getting API keys"""
        
        instructions = """
╔════════════════════════════════════════════════════════════════════╗
║         🔑 API KEY SETUP INSTRUCTIONS                              ║
╚════════════════════════════════════════════════════════════════════╝

1️⃣  ALPHA VANTAGE (ESSENTIAL)
   └─ Get free key: https://www.alphavantage.co/
   └─ Use: Financial fundamentals, earnings, cash flow
   └─ Limit: 5 calls/min (free tier)
   └─ Set in Railway: ALPHA_VANTAGE_KEY

2️⃣  FINNHUB (ESSENTIAL)
   └─ Get free key: https://finnhub.io/
   └─ Use: Government contracts, company news, estimates
   └─ Limit: 60 calls/min (free tier)
   └─ Set in Railway: FINNHUB_KEY

3️⃣  NEWSAPI (RECOMMENDED)
   └─ Get free key: https://newsapi.org/
   └─ Use: Stock news and sentiment analysis
   └─ Limit: 100 calls/day (free tier)
   └─ Set in Railway: NEWS_API_KEY

4️⃣  IEX CLOUD (OPTIONAL)
   └─ Get free key: https://iexcloud.io/
   └─ Use: Real-time quotes and fundamentals
   └─ Limit: 100/month (free tier)
   └─ Set in Railway: IEX_CLOUD_KEY

═════════════════════════════════════════════════════════════════════

HOW TO SET IN RAILWAY:
1. Go to Railway Dashboard
2. Click Scanner-agent → Variables tab
3. Add new variable for each key
4. Name: ALPHA_VANTAGE_KEY, FINNHUB_KEY, etc.
5. Value: Your API key
6. Save & redeploy

═════════════════════════════════════════════════════════════════════
        """
        
        return instructions

def get_api_status():
    """Get current API configuration status"""
    status = {
        'alpha_vantage': '✅' if APIKeysConfig.ALPHA_VANTAGE_KEY else '❌',
        'finnhub': '✅' if APIKeysConfig.FINNHUB_KEY else '❌',
        'newsapi': '✅' if APIKeysConfig.NEWS_API_KEY else '❌',
        'iex_cloud': '✅' if APIKeysConfig.IEX_CLOUD_KEY else '❌'
    }
    return status

# For Railway console testing
if __name__ == '__main__':
    print(APIKeysConfig.get_setup_instructions())
    APIKeysConfig.validate_keys()
