## DEV NOTES

Use `pull_data` to pull basic data into the system:

`python manage.py pull_data <MODEL>`

Run with `--help` option to see what models are supported, e.g.

`python manage.py pull_data --help`

Due to the use of ForeignKeys, some data has to be pulled before other data (e.g. `BodyType` data has to be pulled before `Body` data, because the latter references the former). The following order seems to work well:

 1. Person
 2. BodyType
 3. Body
 4. MatterType
 5. MatterStatus
 6. Matter
 7. VoteType
 8. Event
 9. Action

There is also a `pull_event_items` command that will pull the EventItems for every Event in the system.  However, it currently generates an IntegrityError on my local system because there is an EventItem that references a Matter than I do not have.  This should be handled programatically somewhow (TODO).

There is a `pull_attachments` which will harvest attachment records, but not the actual PDF files. `pull_pdfs` is still pending some functionality in the python-documentcloud library. For development, you will likely only want to pull a portion of the attachment records as it can take several hours to harvest all of them (around 58,000 total).

### Local development setup

#### Install Python 3.4.4

Download installer from https://www.python.org/downloads/release/python-343/

**OR**

Install using [Homebrew](http://brew.sh):

`brew install python3`

**Note**: Whichver of the above you chose, you may need to upgrade virtualenvwrapper.

`sudo pip install virtualenvwrapper --upgrade`

#### Install PostgreSQL

Download and run installer for Mac OS X Version 9.3.9

http://www.enterprisedb.com/products-services-training/pgdownload

    Default installation directory = /Library/PostgreSQL/9.3
    Default data directory /Library/PostgreSQL/9.3/data
    Default Port = 5432
    Use default locale
    
Add the PostgreSQL bin directory to your PATH environment variable:

`PATH=$PATH:/Library/PostgreSQL/9.3/bin`

You may need to add the PostgreSQL lib directory to your DYLD_FALLBACK_LIBRARY_PATH environment variable:

`DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:/Library/PostgreSQL/9.3/lib`

**or**

Install using [Homebrew](http://brew.sh):

`brew install postgres --with-python`

(I installed Postgres with homebrew a long time ago, so can't verify this exact command.)

#### Setup PostgreSQL


Create the `cityhallmonitor` database and `cityhallmonitor` user by executing the `initdb.sh` script.

`$ ./initdb.sh`

This script assumes you've created a Postgres admin user with the same username as your shell login. If that's not the case, use this form instead:

`$ PGUSER="postgres" ./initdb.sh`

If your Postgres admin user has a different name, change the value of `PGUSER`.


        
```
$ createdb -U postgres cityhallmonitor
$ psql -U postgres cityhallmonitor
cityhallmonitor=# CREATE USER cityhallmonitor WITH PASSWORD 'default';
cityhallmonitor=# GRANT ALL PRIVILEGES ON DATABASE "cityhallmonitor" to cityhallmonitor;
cityhallmonitor=# \q
```

Verify you can connect to database as cityhallmonitor user:

```
$ psql -U cityhallmonitor cityhallmonitor
```

#### Setup project

Make virtual environment and install requirements:

```
$ mkvirtualenv --python=/usr/local/bin/python3 cityhallmonitor
$ pip install -r requirements.txt
```

Create database tables:

```
python manage.py syncdb
```

Load sample data fixtures (for now):

```
$ python manage.py loaddata Action.json
$ python manage.py loaddata MatterType.json
```






