#How to use the OATS database

## Introduction

`$ SOME_CODE` A command to enter in the regular linux shell

`>>> SOME_CODE` A command to enter in the python shell.

#### Collections
There are three different collections in the test database which represent the
three different kinds of datasets which are stored.

`cases` collection

`network` collection

`technician` collection

In this tutorial whenever you see `cases/network/technician` means that you have to choose one of them.

## CREATE

Go to /srv/database/data/templates choose one of the templates and save a copy of them to your directory.
```
$ cd /srv/database/templates
$ cp template_file.json name_of_your_created_doc.json
```
Open the file with a texteditor of your choice example:

```
$ vi name_of_your_document.json
```

Edit everything between the two Dollar signs and delete them afterwards like this:

`"$EDIT_THIS$`

to

`"the_text_you_want"`

After you saved the file import it into the desired collection.

```
$ mongoimport --db test --collection cases/network/technician --file /srv/database/data/your_file_name.json
```

`--db test` specifies your database.

`--collection` specifies your collection

`--file` specifies the path to your file


## READ

Export the collection you want to read, as a JSON file.

```
$ mongoexport --db test --collection cases/network/technician --out example.json
```
## UPDATE

Export the collection you want to edit, as a JSON file.
```
$ mongoexport --db test --collection cases/network/technician --out example.json
```
Edit the files you wish to edit and save. Then Import it into the database again.
The `--drop` Option will drop the previous Collection and make certain that no entry exists twice.

```
$ mongoimport --db test --collection cases/network/technician --drop --file /srv/Database/your_file_name.json
```

## DELETE

From the Python Shell, use MongoClient to connect to the running mongod instance, and switch to the test database.

```
$ python

>>>from pymongo import MongoClient
>>>client = MongoClient()
>>>db = client.test
```

Use the `.delete_many` command to delete all documents that match your defined parameters.

```
>>>db.cases/network/technician.delete_many({"INSERT_FIELD1": "INSERT_VALUE1","INSERT_FIELD2": "VALUE2"})
```
