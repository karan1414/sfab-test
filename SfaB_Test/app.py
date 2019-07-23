import os
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

SECRET_KEY = os.urandom (256)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# GCP
CLOUDSQL_USER = os.environ.get("DB_USER")
CLOUDSQL_PASSWORD = os.environ.get("DB_PASS")
CLOUDSQL_DATABASE = os.environ.get("DB_NAME")
CLOUDSQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@127.0.0.1:3306/{dbn}').format (
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
)

LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@localhost/{dbn}?unix_socket=/cloudsql/{con}').format (
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
    con=CLOUDSQL_CONNECTION_NAME,
)

if os.environ.get ('GAE_INSTANCE'):
    SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
else:
    SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# location model to store data
class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer,primary_key=True)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    angle = db.Column(db.Integer)
    direction = db.Column(db.String(100))

# welcome home page 
# this seems to be working when i deploy on gcp
@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Flippingo !!'

# saves the location data

@app.route('/location_save',methods=['POST'])
def location_save():
    location = Location(
    latitude = request.json.get('latitude'),
    longitude = request.json.get('longitude'),
    angle = request.json.get('angle'),
    direction = request.json.get('direction')
    )

    db.session.add(location)
    db.session.commit()

    return jsonify({ "latitude":location.latitude , "longitude" : location.longitude , "angle":location.angle , "direction":location.direction})

# get details of a location by passing latitude and longitude values in json
@app.route('/get_location',methods=['GET'])
def get_location():

    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')

    print(latitude)
    print(longitude)

    loc = Location.query.filter_by(latitude = latitude).first()



    return jsonify({"latitude":loc.latitude , "longitude" : loc.longitude , "angle" : loc.angle , "direction" : loc.direction})


# link to get all of the location data in the table
@app.route('/get_all',methods=['GET'])
def get_all():

   loc = Location.query.all()

   data = []

   print(loc)
   for l in loc:
       data.append({
        "latitude" : l.latitude,
        "longitude" : l.longitude,
        "angle"     : l.angle,
        "direction" : l.direction
        })
    # print(l.latitude)

   return jsonify({"data":data})

# @app.route('/delete_all_location',methods=['DELETE'])
# def delete_all_location():

#     # loc = Location.query.all()
#     # db.session.delete(loc)
#     db.session.query(Location).delete()
#     db.session.commit()

#     return jsonify({"msg":"Delete"})

if __name__ == "__main__":
    db.create_all()
    # app.run(host="0.0.0.0", port=80)
    app.run(host="127.0.0.1", port=5000,debug=True)
