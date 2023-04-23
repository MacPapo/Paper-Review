from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://moonphase:eclipse@db:5432/paper_review"


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
