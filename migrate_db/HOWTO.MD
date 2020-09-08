# Load TIND dump

Once the docker is launched and you have access to the database: 

- Set the port `POSTGRES_PORT=5432`
- Set the host `POSTGRES_HOST=pgsql.epfl.ch`

- Create the list of tables we want to import (go directly to load data if you have already the db.list)
    ```
    pg_restore \
    --verbose \
    --dbname "infoscience-exports" \
    --schema "public" \
    --username "infoscience-exports" \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    -l \
    "/media/del/SSD850EVO1TB/workspace/infoscience-exports-TIND-dumps/backup.sql.tar" > db.list
    ```
- remove session table data
    `sed -i 's/.*TABLE DATA public django_session.*/;&/' db.list  | grep django_session`

- remove cached table data
    `sed -i 's/.*TABLE DATA public generated_export_cache_expires.*/;&/' db.list  | grep generated_export_cache_expires`

- load datas in respect of the db.list (prepare the password)
    ```
    pg_restore \
    --clean \
    --verbose \
    --dbname "infoscience-exports" \
    --schema "public" \
    --username "infoscience-exports" \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --no-owner --role=infoscience-exports \
    -L "/media/del/SSD850EVO1TB/workspace/infoscience-exports-TIND-dumps/db.list" \
    "/media/del/SSD850EVO1TB/workspace/infoscience-exports-TIND-dumps/backup.sql.tar"
    ```
