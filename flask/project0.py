from app import create_app
from app.datafill import fake_data
app = create_app()
with app.app_context():
     fake_data()
