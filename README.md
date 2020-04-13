# SMS : `Save my Session/Soul`

#### Usage of `sms`

    sms [-h] [-v] {db,session} ...

#### Submodules of sms:

* `session` - Deal with session
* `db`      - Deal with Database

#### Usage of `session`

    sms session [-h] {open,view,edit,save} ...

#### submodules of `session`:

* `save` - Save a session
* `open` - Open saved apps for a named session
* `view` - View all saved apps for a names session
* `edit` - Edit a named session

###### Usage of `session save`:

    sms session save [-h] -n NAME [-l | -s | -a]

###### Usage of `session open`:

    sms session open [-h] -n NAME [-l | -s]

###### Usage of `session view`:

    sms session view [-h] [-n NAME | --sessions] -l | -s | -a]

###### Usage of `session edit`:

    sms session edit [-h] -n NAME [-l | -s] -a | -d | --delete-all]


#### Usage of `db`

    sms db [-h] {tables,delete,drop} ...

#### submodules of `db`:

* `tables` - Return all available tables in the Database
* `delete` - Delete Database
* `drop`   - Drop table from Database


###### Usage of `db tables`:

    sms db tables [-h]

###### Usage of `db delete`:

    sms db delete [-h] [-y]

###### Usage of `db drop`:

    sms db drop [-h] [-y] [-t TABLE | -a]


## More information can be available on usage for each module using the `-h` argument.


