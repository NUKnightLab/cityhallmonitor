### Local development setup

#### Install Python 3.4.4

Download installer from https://www.python.org/downloads/release/python-343/

Upgrade virtualenvwrapper, if needed:

`sudo pip install virtualenvwrapper --upgrade`


#### Setup PostgreSQL

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

Create the `cityhallmonitor` database and `cityhallmonitor` user
        
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






