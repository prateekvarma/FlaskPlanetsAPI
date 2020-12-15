from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message


app = Flask(__name__)


# get the absolute path of this very folder
basedir = os.path.abspath(os.path.dirname(__file__))
# use Flask's config manager to tell where the DB is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
# configure JWT's secret key
app.config['JWT_SECRET_KEY'] = 'secret' # change this in production
# Mail configuration setup, using Mailtrap
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'username-here'
app.config['MAIL_PASSWORD'] = 'pwd-here'


# initialize the DB
db = SQLAlchemy(app)
# initialize JWT
jwt = JWTManager(app)
# create an instance of Mail
mail = Mail(app)


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


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    # SQLAlchemy
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message="That email is already registered"), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, password=password, email=email)
        # SQLAlchemy
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@app.route('/login', methods=['POST'])
def login():
    # check if it's a JSON post
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    # Regular form POST
    else:
        email = request.form['email']
        password = request.form['password']
    # check if email & pwd matched in DB, this is SQLAlchemy
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        # create a JWT access token based of email
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Successful', access_token=access_token)
    else:
        return jsonify(message="Incorrect email or password"), 401


@app.route('/retrieve-password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        # Message() here is a constructor, used to build the email
        msg = Message("Your password is: " + user.password,
                      sender="admin@planetapi.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message='Password sent to: ' + email)
    else:
        return jsonify(message="That email does not exit"), 401


@app.route('/planets-details/<int:planet_id>', methods=['GET'])
def planets_details(planet_id: int):
    # SQLAlchemy thing below
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        # Marshmallow serialization of data below
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        # no planets found with that id
        return jsonify(message="No planets found"), 404


# Remember, you can get the access token, returned from login
@app.route('/add-planet', methods=['POST'])
@jwt_required # just this line does the JWT check
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message='That planet already exists'), 409
    else:
        # below line commented since it's already requested above
        # planet_name = request.form['planet_name']
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = float(request.form['mass'])
        radius = float(request.form['radius'])
        distance = float(request.form['distance'])

        # SQLAlchemy
        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message='You added a planet!'), 201


@app.route('/update-planet', methods=['PUT'])
@jwt_required # this is all that's required to do a JWT check
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message="Planet updated"), 202
    else:
        return jsonify(message="No planet found"), 404


if __name__ == '__main__':
    app.run()