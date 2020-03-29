''' 
=======================================================
Step 2 - Climate App 
=======================================================
'''
# == Design a Flask API based on the queries that you have just developed. ==

# SQL and Python needs
import numpy as np 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime
from dateutil.relativedelta import relativedelta, MO
import json
from flask import Flask, jsonify

# == DATABASE ==
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Get Base class.
Base = automap_base()
# Reflect the tables
Base.prepare(engine,reflect=True)
# Save references to the tables
Measurement = Base.classes.measurement 

# == ROUTES ==
# List all routes that are available.

# Create an app.
app = Flask(__name__)

# '/'
# Home page.
@app.route("/")
def home():
    return (
        f"Welcome to Hawaii! <br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/2016-08-18 <br/>"
        f"/api/v1.0/2015-08-18 <br/>"
        f"/api/v1.0/2014-08-18 <br/>"
        f"/api/v1.0/2013-08-18 <br/>"
        f"/api/v1.0/2012-08-18 <br/>"
        f"/api/v1.0/2011-08-18 <br/>"
        f"/api/v1.0/2010-08-18 <br/>"
        f"/api/v1.0/2017-08-18/2016-08-18 <br/>"
        f"/api/v1.0/2016-08-18/2015-08-18 <br/>"
        f"/api/v1.0/2015-08-18/2014-08-18 <br/>"
        f"/api/v1.0/2014-08-18/2013-08-18 <br/>"
        f"/api/v1.0/2013-08-18/2012-08-18 <br/>"
        f"/api/v1.0/2012-08-18/2011-08-18 <br/>"
    )

# Route: '/api/v1.0/precipitation'
# Convert the query results to a dictionary using 'date' as the key and 'prcp' as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query
    prcp_dates = session.query(Measurement.date, Measurement.prcp).all()

    # Not forget close.
    session.close()

    # Create dict and list
    list_prcp = []
    
    for date, prcp in prcp_dates:
        prcp_dict = {}
        prcp_dict["date"] = date 
        prcp_dict["prcp"] = prcp 
        list_prcp.append(prcp_dict)

    return jsonify(list_prcp)

# Route: '/api/v1.0/stations'
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations_num = [Measurement.station, func.count(Measurement.station)]
    count_station = session.query(*stations_num).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    session.close()

    return jsonify(count_station)

# Route: '/api/v1.0/tobs'
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Could not call stations() functions so again...
    stations_num = [Measurement.station, func.count(Measurement.station)]
    count_station = session.query(*stations_num).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    
    high_station = count_station[0][0]
    
    high_temps = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.station == high_station).all()

    # Last year data.
    temps_date_form = datetime.datetime.strptime(high_temps[0][1],'%Y-%m-%d')
    temps_months_ago = temps_date_form - relativedelta(years=1)
    temps_ago_form = temps_months_ago.strftime('%Y-%m-%d')

    # Getting the data.
    temps_date = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date >= temps_ago_form).\
    filter(Measurement.station == high_station).all()

    session.close()

    return jsonify(temps_date)

# == Route: '/api/v1.0/<start>' and '/api/v1.0/<start>/<end>' ==
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# Route: '/api/v1.0/<start>' 
# When given the start only, calculate 'TMIN', 'TAVG', and 'TMAX' for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_range(start):
    # From these date to "present" or last date stored.
    start_dates = [
        {"start": "2016-08-18"},
        {"start": "2015-08-18"},
        {"start": "2014-08-18"},
        {"start": "2013-08-18"},
        {"start": "2012-08-18"},
        {"start": "2011-08-18"},
        {"start": "2010-08-18"}
    ]
    
    session = Session(engine)

    max_temp = session.query(func.max(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).all()

    min_temp = session.query(func.min(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).all()

    session.close()

    for row in range(len(start_dates)):
            search_term = start_dates[row]["start"]

            if search_term == start:
                return jsonify(max_temp, min_temp, avg_temp)

    return jsonify({"error": f"Oops! Date {start} out of range. =("}),404

# Route: '/api/v1.0/<start>/<end>' 
# When given the start and the end date, calculate the 'TMIN', 'TAVG', and 'TMAX' for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,end):
    # Random start, end dates.
    start_end_dates = [
        {"start": "2017-08-18", "end": "2016-08-18"},
        {"start": "2016-08-18", "end": "2015-08-18"},
        {"start": "2015-08-18", "end": "2014-08-18"},
        {"start": "2014-08-18", "end": "2013-08-18"},
        {"start": "2013-08-18", "end": "2012-08-18"},
        {"start": "2012-08-18", "end": "2011-08-18"},
        {"start": "2011-08-18", "end": "2010-08-18"}
    ]

    session = Session(engine)

    max_temp = session.query(func.max(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).\
    filter(Measurement.date >= end).all()

    min_temp = session.query(func.min(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).\
    filter(Measurement.date >= end).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.date <= start).\
    filter(Measurement.date >= end).all()

    session.close()

    for row in range(len(start_end_dates)):
            search_start = start_end_dates[row]["start"]
            search_end = start_end_dates[row]["end"]

            if search_start == start and search_end == end:
                return jsonify(max_temp, min_temp, avg_temp)

    return jsonify({"error": f"Oops! Date {start} and {end} out of range."}) , 404

  # NEVER FORGET
if __name__ == "__main__":
    app.run(debug=True)