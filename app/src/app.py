from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
import sqlalchemy as sa


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://moonphase:eclipse@db:5432/paper_review"

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'bucami'

toolbar = DebugToolbarExtension(app)

# Initialize the database
db = SQLAlchemy()

db.init_app(app)


class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String)


with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("index.html")


@app.route("/about")
def about_page():
    return render_template("about.html")

if __name__ == "__main__":
    app.run()
