from app import create_app, db
from app.utils import import_enrollment_data, create_admin_account

app = create_app()

if __name__ == '__main__':
    # Ensure tables are created
    with app.app_context():
        db.create_all()
        import_enrollment_data('Enrollment example data for Lab8.csv')
        create_admin_account()
  
    app.run()
