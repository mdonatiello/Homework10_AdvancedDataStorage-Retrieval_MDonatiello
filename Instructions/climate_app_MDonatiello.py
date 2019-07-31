import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

year_ago = dt.datetime(2016, 8, 22)
last_date = dt.datetime(2017, 8, 23)
#start_date_calc = calc_temps('2017-08-09','2017-08-23')
#start_date_end_date_calc = calc_temps('2017-08-09', '2017-08-23')

@app.route("/")
def main():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Climate API!<br/>"
        f"-------------------------<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation ---- one-year of precipitation data<br/>"
        f"/api/v1.0/stations ---- a list of all Hawaii weather stations<br/>"
        f"/api/v1.0/tobs ---- one-year of temperature data<br/>" 
        f"-------------------------<br/>"
        f"---- Temperature calculations<br/>"
        f"/api/v1.0/calc_temps/2016-08-22 ---- min, avg and max temperatures from date given and forward<br/>"
        f"/api/v1.0/calc_temps/2016-08-22/2017-08-23 ---- min, avg and max temperatures for date range inclusive of start and end dates</br>"
        f"--------------------------")

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as they key and prcp as the value."""

    results = session.query(measurement.date, measurement.prcp, measurement.station).\
    filter(measurement.date >= year_ago).\
    filter(measurement.date <= last_date).\
    order_by(measurement.date).all()

    all_precipitation = []
    for result in results:
        precipitation_dict = {result.date: result.prcp, "Station": result.station}
#        precipitation_dict["date"] = date
#        precipitation_dict["prcp"] = precipitation
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
##    """Return a JSON list of stations from the dataset."""
    results = session.query(station.name, station.station, station.latitude, station.longitude, station.elevation).all()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
#    """query for the dates and temperature observations from a year from the last data point."""
    results = (session.query(measurement.date, measurement.tobs, measurement.station).\
    filter(measurement.date >= year_ago).\
    filter(measurement.date <= last_date).\
    order_by(measurement.date).all())

    tobs_12_mos = []
    for result in results:
        tobsDict = {result.date: result.tobs, "Station": result.station}
        tobs_12_mos.append(tobsDict)

    return jsonify(tobs_12_mos)


@app.route("/api/v1.0/calc_temps/<start_Date>")
def start(start_Date):
#    """Calculate TMIN, TAVG and TMAX for all dates greater than and equal to the start date."""
    start_date_calcs = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    results = (session.query(*start_date_calcs).\
        filter(measurement.date >= year_ago).\
        group_by(measurement.date).all())

    key_temps = []
    for result in results:
        key_temps_dict = {}
        key_temps_dict["Date"] =  result[0]
        key_temps_dict["Lowest Temperature"] = result[1]
        key_temps_dict["Average Temperature"] = result[2]
        key_temps_dict["Highest Temperature"] = result[3]
        key_temps.append(key_temps_dict)
    return jsonify(key_temps)


@app.route("/api/v1.0/calc_temps/<start_Date>/<end_Date>")
def start_End(start_Date, end_Date):
#    """Calculate TMIN, TAVG and TMAX for all dates greater than and equal to the start date."""
    start_date_end_date_calcs = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    results = (session.query(*start_date_end_date_calcs).\
        filter(measurement.date >= year_ago).\
        filter(measurement.date <= last_date).\
        group_by(measurement.date).all())

    key_temps2 = []
    for result in results:
        key_temps2_dict = {}
        key_temps2_dict["Date"] =  result[0]
        key_temps2_dict["Lowest Temperature"] = result[1]
        key_temps2_dict["Average Temperature"] = result[2]
        key_temps2_dict["Highest Temperature"] = result[3]
        key_temps2.append(key_temps2_dict)
    return jsonify(key_temps2)

if __name__ == "__main__":
        app.run(debug=True)
