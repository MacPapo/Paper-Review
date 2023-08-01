from app import fake
from faker import Faker
from app.modules.crypt import Crypt
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def random_date():
    Faker.seed(0)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 18)
    #generate 10 rows for tablee users
    user = User(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birthdate=fake.date_between(start_date=start_date, end_date=end_date),
            email=fake.email(),
            password_hash=generate_password_hash(fake.password()),
            sex=fake.random_element(elements=("M", "F", "Other")),
            nationality=fake.country(),
            phone=fake.phone_number(),
            department=fake.job(),
            type=fake.random_element(elements=("researcher", "reviewer")),
        )
    db.session.add(user)
