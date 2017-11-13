import pymongo
from pymongo import MongoClient
import json


client = MongoClient()
db = client.test
cases = db.cases

def net_health():

  new_cases =  db.cases.find({"status":"New"}).count()
  auto_cases = db.cases.find({"status":"solution_deployed"}).count()
  techreq_cases = db.cases.find({"status":"technician_needed"}).count()
  tech_cases = db.cases.find({"status":"technician_called"}).count()

  open_cases = new_cases + auto_cases + techreq_cases + tech_cases

  return open_cases