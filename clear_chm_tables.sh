#!/usr/bin/env bash
declare -a tables=("cityhallmonitor_mattersponsor" "cityhallmonitor_bodytype" "cityhallmonitor_subscription" "cityhallmonitor_document" "cityhallmonitor_matter" "cityhallmonitor_person" "cityhallmonitor_matterattachment" "cityhallmonitor_mattertype" "cityhallmonitor_body" "cityhallmonitor_matterstatus")
for table in ${tables[@]}; do
 echo "drop table ${table} cascade;" | python ./manage.py dbshell;
done;
