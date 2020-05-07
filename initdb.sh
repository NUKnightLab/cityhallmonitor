#!/bin/sh
docker-compose run pg psql -U postgres -h pg postgres -c "DROP DATABASE IF EXISTS cityhallmonitor"
docker-compose run pg psql -U postgres -h pg postgres -c "CREATE DATABASE cityhallmonitor"
docker-compose run pg psql -U postgres -h pg postgres -c "DROP USER IF EXISTS cityhallmonitor"
docker-compose run pg psql -U postgres -h pg postgres -c "CREATE USER cityhallmonitor WITH PASSWORD 'cityhallmonitor';"
docker-compose run pg psql -U postgres -h pg postgres -c 'GRANT ALL PRIVILEGES ON DATABASE "cityhallmonitor" to cityhallmonitor;'
docker-compose run web ./manage.py migrate
docker-compose run web ./manage.py loaddata fixtures/MatterType.json
