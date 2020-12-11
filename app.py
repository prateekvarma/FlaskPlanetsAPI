from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# get the absolute path of this very folder
basedir = os.path.abspath(os.path.dirname(__file__))
# use Flask's config manager to tell where the DB is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
# initialize the DB
db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/yolo')
def yolo():
    return 'You only live once!'


if __name__ == '__main__':
    app.run()