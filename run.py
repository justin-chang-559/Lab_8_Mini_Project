from app import create_app, db
from app.utils import import_enrollment_data

app = create_app()

if __name__ == '__main__':
    # Ensure tables are created
    with app.app_context():
        db.create_all()
        import_enrollment_data('Enrollment example data for Lab8.csv')
        
    app.run()
