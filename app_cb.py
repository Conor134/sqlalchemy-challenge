import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f" /api/v1.0/start date(yyyy-mm-dd)<br/>"
        f"/api/v1.0/start date (yyyy-mm-dd)/end date (yyyy-mm-dd)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()
   
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precipitation.append(precip_dict)

    session.close()

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)


    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    results = session.query(*sel).all()
   
    stations = []
    for station,name,latitude,longitude,elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation

        stations.append(station_dict)

    session.close()

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers

    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = (dt.datetime.strptime(end_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')


    sel = [Measurement.date,Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date  >= query_date).all()
   
    temps = []
    for date, temp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = temp

        temps.append(temp_dict)

    session.close()

    return jsonify(temps)


@app.route("/api/v1.0/<start>")
def temps_start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()

    start_period = []
    for date, min, avg, max in results:
        start_dict = {}
        start_dict["date"] = date
        start_dict["Min Temp"] = min
        start_dict["Avg Temp"] = avg
        start_dict["Max Temp"] = max

        start_period.append(start_dict)

    session.close()

    return jsonify(start_period)


@app.route("/api/v1.0/<start>/<end>")
def temps_start_end_date(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)
 
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    period = []
    for date, min, avg, max in results:
        period_dict = {}
        period_dict["date"] = date
        period_dict["min"] = min
        period_dict["avg"] = avg
        period_dict["max"] = max

        period.append(period_dict)

    session.close()

    return jsonify(period)


if __name__ == '__main__':
    app.run(debug=True)
