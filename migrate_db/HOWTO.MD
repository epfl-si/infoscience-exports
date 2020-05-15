# Load TIND dump

Once the docker is launched and you have access to the database: 

- Set the port `POSTGRES_PORT=25432`

- Create the list of tables we want to import (go directly to load data if you have already the db.list)
    ```
    pg_restore \
    --verbose \
    --dbname "infoscience_exports" \
    --schema "public" \
    --username "postgres" \
    --host "localhost" \
    --port "$POSTGRES_PORT" \
    -l \
    "/media/del/SSD850EVO1TB/workspace/infoscience-exports/backup/db.list" > db.list
    ```
- remove session table
    `sed -i 's/.*TABLE DATA public django_session.*/;&/' db.list  | grep django_session`

- load datas in respect of the db.list
    ```
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
    ```
