#!/usr/bin/env bash

# fetch the data
FILE=chm_prd_20160112_data.gz
URL=http://archive.knilab.com.s3.amazonaws.com/cityhallmonitor/$FILE
if [ ! -f "./$FILE" ]; then
    echo "Fetching file: $URL"
    curl -O $URL
fi

# clear the tables
declare -a tables=("cityhallmonitor_mattersponsor" "cityhallmonitor_bodytype" "cityhallmonitor_subscription" "cityhallmonitor_document" "cityhallmonitor_matter" "cityhallmonitor_person" "cityhallmonitor_matterattachment" "cityhallmonitor_mattertype" "cityhallmonitor_body" "cityhallmonitor_matterstatus")
for table in ${tables[@]}; do
 echo "drop table ${table} cascade;" | docker-compose run pg psql -h pg cityhallmonitor;
done;

# load the data
gzcat chm_prd_20160112_data.gz | docker-compose run pg psql -h pg cityhallmonitor;
