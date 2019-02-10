import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt 
# from datetime import strptime 

from flask import Flask, jsonify
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Surf's Up Climate API!<br/>"
        f"Available Routes (Use YYYY-MM-DD format for start and end dates):<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation records"""
    # Query all Measurement records
    sel = [Measurement.id, Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs]
    results = session.query(*sel).all()

    # Create a dictionary from the row data and append to a list of all_precip
    all_precip = []
    for precip in results:
        precip_dict = {}
        precip_dict["id"] = precip.id
        precip_dict["station"] = precip.station
        precip_dict["date"] = precip.date
        precip_dict["prcp"] = precip.prcp
        precip_dict["tobs"] = precip.tobs
        all_precip.append(precip_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations data including the station, name, and location"""
    # Query all stations
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observation data"""

    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year, month, day = lastdate.split('-')
    year = str(int(year)-1)
    year_ago = year + '-' + month + '-' + day

    # Query all tobs since a year before the last observation
    results = session.query(Measurement).filter(Measurement.date >= year_ago).all()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for tobs in results:
        tobs_dict = {}
        tobs_dict["id"] = tobs.id
        tobs_dict["station"] = tobs.station
        tobs_dict["date"] = tobs.date
        tobs_dict["prcp"] = tobs.prcp
        tobs_dict["tobs"] = tobs.tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<since_date>")
def tobs_by_start(since_date):
    """Return a list of min, average, and max temperature observation data since start date"""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Query all tobs since the start date
    start_results = session.query(*sel).filter(Measurement.date >= since_date).all()

    # Convert list of tuples into normal list
    all_start = list(np.ravel(start_results))

    # Create a dictionary from the row data and append to a list
    return jsonify(all_start)


@app.route("/api/v1.0/<start_date>/<end_date>", methods=['GET'])
def tobs_by_start_end(start_date, end_date):
    """Return a list of min, average, and max temperature observation data between start amd end"""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # start_date = dt.strptime(start, "%Y-%m-%d").date()
    # end_date = dt.strptime(end, "%Y-%m-%d").date()
    # start_date = start
    # end_date = end 

    # Query all tobs between the start and end dates
    start_end_results = session.query(*sel).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert list of tuples into normal list
    all_start_end = list(np.ravel(start_end_results))

    # Create a dictionary from the row data and append to a list
    # return jsonify({"error": f"not found."}), 404
    return jsonify(all_start_end)

if __name__ == "__main__":
    app.run(debug=True)

