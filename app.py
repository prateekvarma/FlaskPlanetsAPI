from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)


# get the absolute path of this very folder
basedir = os.path.abspath(os.path.dirname(__file__))
# use Flask's config manager to tell where the DB is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
# initialize the DB
db = SQLAlchemy(app)


from models import Planet, User, user_schema, users_schema, planet_schema, planets_schema


# create a custom Flask CLI command to create a DB, using a decorator.
# **Just write "flask db_create on CLI to run this**"
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created!')


# custom flask CLI command to delete the DB. db_drop is sqlalchemy function
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='sol',
                     mass=3.258e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='Venus',
                     planet_type='Class k',
                     home_star='sol',
                     mass=4.867e24,
                     radius=3760,
                     distance=67.24e6)

    earth = Planet(planet_name='Earth',
                     planet_type='Class M',
                     home_star='sol',
                     mass=5.972e24,
                     radius=3959,
                     distance=92.96e6)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='William',
                     last_name='Herschel',
                     email='test@test.com',
                     password='password')

    db.session.add(test_user)
    db.session.commit()
    print('Database Seeded!')


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/yolo')
def yolo():
    return 'You only live once!'


@app.route('/planets', methods=['GET'])
def planets():
    # By SQLAlchemy
    planets_list = Planet.query.all()
    # marshmallow's serialization
    result = planets_schema.dump(planets_list)
    return jsonify(result)


if __name__ == '__main__':
    app.run()