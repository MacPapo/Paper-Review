from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

# Initialize the database
db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://moonphase:eclipse@db:5432/paper_review'

db.init_app(app)

class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String)


with app.app_context():
    db.create_all()

@app.route("/")
def home_page():
    return "<p>Hello from Home page!</p>"


@app.route("/hello")
def hello_world():
    return "<p>Hello from hello page!</p>"


@app.route("/about")
def about_page():
    return "<p>Hello from about page!</p>"


if __name__ == "__main__":
    app.run()
