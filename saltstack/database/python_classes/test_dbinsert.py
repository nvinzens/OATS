import pytest
import db_insert
import pymongo
from pymongo import MongoClient

def test_db_insert_args():
  event = "testevent"
  device = "testdevice"
  solution = "testsolution"
  client = MongoClient()
  db = client.test
  insert_test = db_insert.main(event, device, solution)
  db.cases.delete_many({"case_nr": insert_test})
  assert insert_test == event + device + solution