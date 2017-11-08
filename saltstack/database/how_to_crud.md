#How to use the SA_AT Database

## Introduction

`$ SOME_CODE` A command to enter in the regular linux shell
`>>> SOME_CODE` A command to enter in the python shell.

#### Collections
There are three different Collections in the Test Database which represent the
three different kinds of datasets which are stored.

`cases` Collection  

`network` Collection

`technician` Collection

`cases/network/technician` means that you have to choose one of them.

## CREATE

Go to /srv/database/templates choose one of the templates and save a copy of them to your directory.
```
cd /srv/database/templates
cp new_file.json name_of_your_document.json
```
Open the file with a texteditor of your choice example:
```
vi name_of_your_document.json
```
Edit everything between the two Dollar signs and delete them afterwards like this:

`"$EDIT_THIS$`

to

`"the_text_you_want"`

After you saved the file import it into the desired collection.
```
$ mongoimport --db test --collection cases/network/technician --file /srv/Database/your_file_name.json
```

## READ

Export the collection you want to read, as a JSON file of your choice.

```
$ mongoexport --db test --collection cases/network/technician --out example.json
```
## UPDATE

Export the collection you want to edit, as a JSON file of your choice.
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
