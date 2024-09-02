# Import the dependencies.


import numpy as np
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.engine import URL

import sqlalchemy 
import datetime as dt
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func 

from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################


engine = create_engine("sqlite:///Resources/hawaii.sqlite")



# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Measure = Base.classes.measurement
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
        """List all available api routes."""
        return(        
            f"Available Routes:<br/>"
            f"<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end<br/>"
            f"<br/>"
            f"Note: to access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        
        """Return a list of precipitation (prcp)and date (date) data"""

        precpitation_query_results = session.query(Measure.prcp, Measure.date).all()

        session.close()

        precipitaton_query_values = []
        for prcp, date in precpitation_query_results:
            precipitation_dict = {}
            precipitation_dict["precipitation"] = prcp
            precipitation_dict["date"] = date
            precipitaton_query_values.append(precipitation_dict)

        return jsonify(precipitaton_query_values) 

@app.route("/api/v1.0/stations")
def station(): 

    session = Session(engine)

    """Return a list of stations from the database""" 
    station_query_results = session.query(Station.station,Station.id).all()

    session.close()  
    
    stations_values = []
    for station, id in station_query_results:
        stations_values_dict = {}
        stations_values_dict['station'] = station
        stations_values_dict['id'] = id
        stations_values.append(stations_values_dict)
    return jsonify (stations_values) 

@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(engine)

    """Return a list of dates and temps observed for the most active station for the last year of data from the database""" 

    last_year_query_results = session.query(Measure.date).\
        order_by(Measure.date.desc()).first() 
    
    print(last_year_query_results)

    last_year_query_values = []
    for date in last_year_query_results:
        last_year_dict = {}
        last_year_dict["date"] = date
        last_year_query_values.append(last_year_dict) 
    print(last_year_query_values)

    query_start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
    print(query_start_date) 

    active_station= session.query(Measure.station, func.count(Measure.station)).\
        order_by(func.count(Measure.station).desc()).\
        group_by(Measure.station).first()
    most_active_station = active_station[0] 

    session.close() 

    print(most_active_station)
 

    dates_tobs_last_year_query_results = session.query(Measure.date, Measure.tobs, Measure.station).\
        filter(Measure.date > query_start_date).\
        filter(Measure.station == most_active_station) 
    

    dates_tobs_last_year_query_values = []
    for date, tobs, station in dates_tobs_last_year_query_results:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        dates_tobs_last_year_query_values.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_query_values)

@app.route("/api/v1.0/<start>")

def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""


    start_date_tobs_results = session.query(func.min(Measure.tobs),func.avg(Measure.tobs),func.max(Measure.tobs)).\
        filter(Measure.date >= start).all()
    
    session.close() 


    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)


@app.route("/api/v1.0/<start>/<end>")


def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
    


    start_end_date_tobs_results = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
        filter(Measure.date >= start).\
        filter(Measure.date <= end).all()

    session.close()
  

    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)
   
if __name__ == '__main__':
    app.run(debug=True) 