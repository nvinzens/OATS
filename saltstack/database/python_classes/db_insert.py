import pymongo
from pymongo import MongoClient
import datetime
import json


client = MongoClient()
db = client.test
cases = db.cases

def insert(event, device, solution):

  new_cases = {
    "case_nr": "GENERATE",
    "Event": event,
    "Description": "Event description",
    "Status": "New",
    "created": datetime.datetime.utcnow(),
    "last_updated": datetime.datetime.utcnow(),
    "technician": "not_called",
    "Sender_Device": device,
    "Solution_tried": {
    "Solution": solution
    }
  }

  cases.insert_one(new_cases)
