import pymongo
from pymongo import MongoClient
import datetime
import json


client = MongoClient()
db = client.test
cases = db.cases

def insert(Event, Device, Solution):

  new_cases = {
    "case_nr": "GENERATE",
    "Event": Event,
    "Description": "Event description",
    "Status": "New",
    "created": datetime.datetime.utcnow(),
    "last_updated": datetime.datetime.utcnow(),
    "technician": "not_called",
    "involved_devices": {
    "host_name": Device
    },
    "Solution_tried": {
    "Solution": Solution
    }
  }

  cases.insert_one(new_cases)
