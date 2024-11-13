from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize the extensions without binding them to the app instance yet
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap3')  # Create admin instance without binding to app
login_manager.login_view = 'login'  # Redirects unauthenticated users to the login page

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Bind the app instance to the extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize admin with the app
    admin.name = 'Admin Mode'
    admin.url = '/admin_panel'
    admin.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from app.models import User, Course, Enrollment
        
        # Add views to admin
        admin.add_view(ModelView(User, db.session))
        admin.add_view(ModelView(Course, db.session))
        admin.add_view(ModelView(Enrollment, db.session))
        
        # Create all database tables
        db.create_all()
    
    # Import routes after initializing extensions
    from app.routes import init_routes
    init_routes(app)
    
    # Define user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app