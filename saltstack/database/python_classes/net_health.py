import pymongo
from pymongo import MongoClient
import json
import bson
from bson.son import SON


client = MongoClient()
db = client.test
cases = db.cases

def net_health():

  new_cases =  db.cases.find({"Status":"New"}).count()
  auto_cases = db.cases.find({"Status":"solution_deployed"}).count()
  techreq_cases = db.cases.find({"Status":"technician_needed"}).count()
  tech_cases = db.cases.find({"Status":"technician_called"}).count()

  open_cases = new_cases + auto_cases + techreq_cases + tech_cases

  pipeline = [
    {"$group": {"Device": "Sender_Device", "count": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])}
  ]

  involved_devices = db.cases.aggregate(pipeline)

  return open_cases