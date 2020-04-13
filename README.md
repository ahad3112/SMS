# SMS : `Save my Session/Soul`

#### Usage of `sms`

    sms [-h] [-v] {db,session} ...

#### Submodules of sms:

* `db`      - Deal with Database
* `session` - Deal with session

#### Usage of `db`

    sms db [-h] {tables,delete,drop} ...

#### submodules of `db`:

* `tables` - Return all available tables in the Database
* `delete` - Delete Database
* `drop`   - Drop table from Database

#### Usage of `session`

    sms session [-h] {open,view,edit,save} ...

#### submodules of `session`:

* `save` - Save a session
* `open` - Open saved apps for a named session
* `view` - View all saved apps for a names session
* `edit` - Edit a named session

###### usafe of `session save`:

    sms session save [-h] -n NAME [-l | -s | -a]

###### usafe of `session open`:

    sms session open [-h] -n NAME [-l | -s]

###### usafe of `session view`:

    sms session view [-h] [-n NAME | --sessions] -l | -s | -a]

###### usafe of `session edit`:

    sms session edit [-h] -n NAME [-l | -s] -a | -d | --delete-all]


## More information can be available on usage for each module using the `-h` argument.


