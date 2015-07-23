#!/bin/sh
dropdb --if-exists cityhallmonitor
createdb cityhallmonitor
dropuser --if-exists cityhallmonitor
psql cityhallmonitor -c "CREATE USER cityhallmonitor WITH PASSWORD 'default';"
psql cityhallmonitor -c 'GRANT ALL PRIVILEGES ON DATABASE "cityhallmonitor" to cityhallmonitor;'
