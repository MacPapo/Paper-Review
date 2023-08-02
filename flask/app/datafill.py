from app import db
from faker import Faker
from werkzeug.security import generate_password_hash
from app.models import User
from datetime import datetime, timedelta

def random_user(fake):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 18)
    #generate 10 rows for tablee users
    for _ in range(10):
        name = fake.name()
        words = name.split()
        first_name = ' '.join(words[:-1])
        last_name = words[-1]
        user = User(
            uid = fake.bothify(text='???????????????'),
            username=name,
            first_name=first_name,
            last_name=last_name,
            birthdate=fake.date_between(start_date=start_date, end_date=end_date),
            email=fake.email(),
            password_hash=generate_password_hash(fake.password()),
            sex=fake.random_element(elements=("M", "F", "Other")),
            nationality=fake.country(),
            phone="+" + fake.phone_number(),
            department=fake.random_element(elements=("Economia", "Informatica e Statistica", "Umanistico","Asia e Africa Mediterranea")),
            type=fake.random_element(elements=("researcher", "reviewer")),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.session.add(user)
    db.session.commit()


#def random_pdf(fake):


def fake_data():
    faker = Faker()
    faker.locale = 'it_IT'
    Faker.seed(0)

    random_user(faker)
    random_pdf(faker)
