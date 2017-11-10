"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

import sys

# Date handling 
import arrow   
from dateutil import tz  # For interpreting local times

# Mongo database
import pymongo
from pymongo import MongoClient


import config
CONFIG = config.configuration()


MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST, 
    CONFIG.DB_PORT, 
    CONFIG.DB)


print("Using URL '{}'".format(MONGO_CLIENT_URL))


###
# Globals
###

app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY

####
# Database connection per server process
###

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)



###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  g.memos = get_memos()
  for memo in g.memos: 
      app.logger.debug("Memo: " + str(memo))
  return flask.render_template('index.html')


# create.html connect to this function and this function put the information into db database

@app.route("/create") #connect to the page
def create():
  app.logger.debug("Create")
  return flask.render_template('create.html')

@app.route("/_create_memo")  #function that create the memo
def create_memo():
    input_date = flask.request.args.get("input_date","2017-01-01T00:00:00",type=str)
    date = arrow.get(input_date).isoformat()
    text = flask.request.args.get("input_text","Hello!",type=str)
	
    record = { "type": "dated_memo", 
           "date":  date,
           "text": text
          }
    collection.insert(record)
    return flask.jsonify()

@app.route("/_delete_memo",methods=["POST"])
def delete_memo():
    delete = flask.request.form["delete"]
    delete2 = delete.split(",")
    date = delete2[0]
    text = delete2[1]
    collection.remove({"text":text},{"date":date})
    return index()


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """

    try:
        then = arrow.get(date).replace(tzinfo='local')
        now = arrow.now().replace(tzinfo='local')
        if then.shift(days=-1).date() == now.date():
            human = "Tomorrow"
        elif now.shift(days=-1).date() == then.date():
            human = "Yesterday"
        elif then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
    except: 
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    #collection.find({}).sort({"date":1})
    for record in collection.find( { "type": "dated_memo" } ).sort("date", pymongo.ASCENDING):
        record['date'] = arrow.get(record['date']).isoformat()
        del record['_id']
        records.append(record)
	#return sorted(records, key=date)
    return records 


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")

    
