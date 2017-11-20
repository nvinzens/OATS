import sys
import pymongo
from pymongo import MongoClient
import json
import pprint
from bson.son import SON

client = MongoClient()
db = client.oatsdb

def main():

  new_cases =  db.cases.find({"Status":"New"}).count()
  auto_cases = db.cases.find({"Status":"solution_deployed"}).count()
  techreq_cases = db.cases.find({"Status":"technician_needed"}).count()
  tech_cases = db.cases.find({"Status":"technician_called"}).count()

  open_cases = new_cases + auto_cases + techreq_cases + tech_cases

  pipeline = [
    {"$unwind": "$Sender_Device"},
    {"$group": {"_id": "$Sender_Device", "Unresolved Cases": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])}
  ]
  pprint.pprint(list(db.cases.aggregate(pipeline)))

  print "The Number of unresolved Cases is: " + str(open_cases)

  return open_cases

if __name__ == "__main__":
    main(sys.argv)