"""
Nose tests for vocab.py
""" 
import flask_main
import nose    # Testing framework
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

###
# connect to the database
###

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
# End of import, start the test
###


col = collection.count()

def test_saving():
    """
    Nothing is present in an empty word list
    """
    record1 = { "type": "dated_memo", 
           "date":  arrow.utcnow(),
           "text": "This is a sample memo"
          }
    collection.insert(record1)
    assert collection.count() == col + 1
    

#Test listing and whether the result is show on the isoformat
def test_listing():
    record1 = { "type": "dated_memo", 
           "date":  arrow.now(),
           "text": "This is a sample memo"
          }
    collection.insert(record1)
    assert collection.find() == { "_id" : ObjectId("5a0507a567a9da222efae606"), "text" : "This is a sample memo", "type" : "dated_memo", "date" : arrow.now().isoformat() }



def test_delete():
    record1 = { "type": "dated_memo", 
           "date":  "2017-11-08",
           "text": "Hello, Yesterday"
          }
    record2 = { "type": "dated_memo", 
           "date":  "2017-11-09",
           "text": "Hello, Today"
          }
    record3 = { "type": "dated_memo", 
           "date":  "2017-11-10",
           "text": "Hello, Tomorriw"
          }
    collection.insert(record1)
    collection.insert(record2)
    collection.insert(record3)
    assert collection.count() == 3
    collection.remove({"date":"2017-11-08"})
    assert collection.count() == 2


def test_humanize():
    assert humanize_arrow_date("2017-11-08") == "Yesterday"
    assert humanize_arrow_date("2017-11-09") == "Today"
    assert humanize_arrow_date("2017-11-10") == "Tomorrow"

