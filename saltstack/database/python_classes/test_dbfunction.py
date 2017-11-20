import pytest
import pymongo
from pymongo import MongoClient
import db_insert
import net_health

def test_db_insert_args():
  errors = []
  event = "testevent"
  device = "testdevice"
  solution = "testsolution"
  client = MongoClient()
  db = client.oatsdb
  insert_test = db_insert.main(event, device, solution)
  if not insert_test == event + device + solution:
      errors.append("Returned Case ID incorrect")
  if not db.cases.find({"case_nr": insert_test}).count() > 0:
      errors.append("Case not inserted into Database")
  db.cases.delete_many({"case_nr": insert_test})
  assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_net_health():
  client = MongoClient()
  db = client.oatsdb
  insert_test = db_insert.main("testevent", "testdevice", "testsolution")
  unresolved_cases = net_health.main()
  db.cases.delete_many({"case_nr": insert_test})
  assert unresolved_cases > 0
