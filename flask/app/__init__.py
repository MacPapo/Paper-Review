from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bucami'
app.debug = True

toolbar = DebugToolbarExtension(app)

from app import routes
