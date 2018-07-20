from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from validators import validators

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/alayatodo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.before_request
def before_request():
    g.validators = validators
    g.messages = []


db = SQLAlchemy(app)

import alayatodo.views
