import sys
import pymongo
from pymongo import MongoClient
import datetime
import json

client = MongoClient()
db = client.oatsdb

def main(evarg, devarg, solarg):

  event = evarg
  device = devarg
  solution = solarg

  case_id = event + device + solution

  new_case = {
    "case_nr": case_id,
    "Event": event,
    "Description": "Event description",
    "Status": "New",
    "created": datetime.datetime.utcnow(),
    "last_updated": datetime.datetime.utcnow(),
    "technician": "not_called",
    "Sender_Device": device,
    "Solution": solution
  }

  try:
    db.cases.insert_one(new_case)
    print "\nCase inserted successfully\n"

  except Exception, e:
      print str(e)

  return case_id

if __name__ == "__main__":
    main(sys.argv)