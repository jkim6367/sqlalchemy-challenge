#import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime , timedelta,date
import time
import datetime as dt
#from flask_optional_routes import OptionalRoutes



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = scoped_session(sessionmaker(engine))


#res = session.query(Passenger.name,Passenger.age, Passenger.sex).all()


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
            f"Welcome to the Trip Planning Climate API!<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation</br>"
            f"/api/v1.0/stations</br>"
            f"/api/v1.0/tobs </br>"
            f"/api/v1.0/tobs/start_date and /api/v1.0/tobs/start_date/end_date</br>" 
            f"Enter the start and end dates in YYYY-MM-dd format for the date query"
    )
def get_year_ago():
	n=session.query(func.max(Measurement.date)).all()
	date_str=n[0][0]
	formatter_string = "%Y-%m-%d" 
	datetime_object = datetime.strptime(date_str, formatter_string)
	date_object = datetime_object.date()
	year_ago= date_object -dt.timedelta(days=365)
	return(year_ago)

@app.route("/api/v1.0/precipitation")
def prcp():
    """Return the precipitation data for one year form the Max date"""
    
    year_ago=get_year_ago()    
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago).all()
    #results = df.name
    # Convert list of tuples into normal list
    prcp = {date:prcp for date,prcp in results}
    return jsonify(prcp)
@app.route("/api/v1.0/stations")
def stations():
	stat_df= pd.DataFrame(session.query(Station.station,Station.longitude,Station.latitude).all())
	stat=stat_df.to_dict('records')
	return jsonify(stat)
 
@app.route("/api/v1.0/tobs")
def tobs():
	#n=session.query(func.max(Measurement.date)).all()
	#date_str=n[0][0]
	#formatter_string = "%Y-%m-%d" 
	#datetime_object = datetime.strptime(date_str, formatter_string)
	#date_object = datetime_object.date()
	#year_ago= date_object -dt.timedelta(days=365)
	year_ago=get_year_ago()
	tobs_df=pd.DataFrame(session.query(Measurement.date,
		Measurement.tobs)\
   .filter(Measurement.date>= year_ago).all())
	tobs_dict= tobs_df.to_dict('records')
	return jsonify(tobs_dict)
@app.route('/api/v1.0/tobs/<start_date>', defaults={'end_date': None})
@app.route('/api/v1.0/tobs/<start_date>/<end_date>')
def tobd_by_date(start_date,end_date):
 
    if end_date == None:
    	tmin,tavg,tmax=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).one()
    	return(f"Min Value{tmin} , Max Temp is {tmax} ,Avg Temp is {tavg}")
    else :
        tmin,tavg,tmax=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).one()
        return(f"Min Value{tmin} , Max Temp is {tmax} ,Avg Temp is {tavg}")
if __name__ == '__main__':
    app.run(debug=True)