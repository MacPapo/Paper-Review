from flask import Flask

app = Flask(__name__)


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
