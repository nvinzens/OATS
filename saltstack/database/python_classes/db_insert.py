import pymongo
from pymongo import MongoClient
import datetime
import json


client = MongoClient()
db = client.test
cases = db.cases

def insert():

  new_cases = {
    "case_nr": "GENERATE",
    "Event": "{{ data['event'] }}",
    "Description": "Event description",
    "Status": "New",
    "created": datetime.datetime.utcnow(),
    "last_updated": datetime.datetime.utcnow(),
    "technician": "not_called",
    "involved_devices": {
    "host_name": "{{ data['device'] }}"
    },
    "Solution_tried": {
    "Solution": "{{ data['SLS'] }}"
    }
  }

  cases.insert_one(new_cases)
