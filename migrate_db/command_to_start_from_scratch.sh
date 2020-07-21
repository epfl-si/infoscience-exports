#!/bin/bash
# This file is obsolete and was used by the dev to set his own Postgres installation
# #toremove
set -x

POSTGRES_PORT=25432

sudo -u postgres psql -h localhost -p $POSTGRES_PORT <<EOF
\x
create user django;
drop database infoscience_exports;
create database infoscience_exports;
grant all privileges on database infoscience_exports to django;
EOF

# create list of operations
pg_restore \
--clean \
--verbose \
--no-password \
--dbname "infoscience_exports" \
--schema "public" \
--username "postgres" \
--host "localhost" \
--port "$POSTGRES_PORT" \
-l \
"/media/del/SSD850EVO1TB/workspace/infoscience-exports/backup/db.list" > db.list

# remove session table
sed -i 's/.*TABLE DATA public django_session.*/;&/' db.list  | grep django_session

- remove cached table data
    `sed -i 's/.*TABLE DATA public generated_export_cache_expires.*/;&/' db.list  | grep generated_export_cache_expires`

# load datas
pg_restore \
--clean \
--verbose \
--dbname "infoscience_exports" \
--schema "public" \
--username "django" \
--host "localhost" \
--port "$POSTGRES_PORT" \
-L "/media/del/SSD850EVO1TB/workspace/infoscience-exports/backup/db.list" \
"/media/del/SSD850EVO1TB/workspace/infoscience-exports/backup/backup.sql.tar"

# clean
rm ./db.list
