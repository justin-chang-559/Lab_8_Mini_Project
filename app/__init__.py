from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize the extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirects unauthenticated users to the login page

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Import models after initializing db to avoid circular imports
    from app.models import User

    # Define user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize routes
    from app.routes import init_routes
    init_routes(app)

    return app
