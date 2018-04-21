import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Create an engine to a SQLite database file called `hawaii.sqlite`
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# error fix from here: 
# https://bitbucket.org/zzzeek/sqlalchemy/issues/3449/automap_base-fails-on-my-database
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    name = referred_cls.__name__.lower() + "_ref"
    return name

# reflect the tables
Base.prepare(
    engine, reflect=True,
    name_for_scalar_relationship=name_for_scalar_relationship
)

# Save reference to the tables
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to Sonia's Weather App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


# Query for the dates and precipitation values from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the json representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    #query
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= '2016-08-23').order_by(Measurements.date)
    
    #convert to dictionary 
    precipitation = []
    for p in results:
        prcp_dict = {}
        prcp_dict["date"] = p.date
        prcp_dict["prcp"] = p.prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # query 
    station_names = session.query(Stations.name).all()

    return jsonify(station_names)

# Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    # Query all tobs values
    tobs = session.query(Measurements.tobs).all()

    return jsonify(tobs)

# Return a json list of the minimum temperature, the average temperature, and the max 
# temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for 
# all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    temperatures = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).all()

    return jsonify(temperatures)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
# between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temperatures_start_end(start, end):
    temperatures = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).\
                filter(Measurements.date <= end).all()

    return jsonify(temperatures)

    
if __name__ == "__main__":
    app.run(debug=True)