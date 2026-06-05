"""
US Stock Scanner - Main Application File
Scans 3,000+ US stocks for 7-reason PLTR/RKLB pattern matches
Shows most matched stocks + cheapest high-quality stocks
"""

from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
