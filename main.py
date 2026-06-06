import os
from flask import Flask
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler

# Import db from app_models - DON'T create a new one!
from app_models import db

def create_app():
    app = Flask(__name__, template_folder='.')
    app.config.from_object(Config)
    
    # Initialize the existing db instance with the app
    db.init_app(app)
    
    # Import and register blueprints BEFORE app context
    from app_routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
