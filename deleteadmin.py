from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Query the admin user
    admin_user = User.query.filter_by(username='admin').first()
    
    if admin_user:
        db.session.delete(admin_user)  # Delete the user
        db.session.commit()  # Commit the changes
        print("Admin user deleted successfully.")
    else:
        print("Admin user not found.")
