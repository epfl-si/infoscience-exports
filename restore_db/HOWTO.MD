# pour lancer
`docker-compose up`

# pour se logger / debug
`psql -h localhost -U postgres -d postgres`
ou
terminal -> `pgadmin4`

# Init & Run
`/home/del/workspace/infoscience-exports/restore_db/command.sh`

# Post process
- Deactivate custom options in docker-compose -> command
- Run ANALYZE afterwards.

# Divers
- from pgadmin
    ```
    /usr/bin/pg_restore --host 127.0.0.1 --port 5432 --username "postgres" --dbname "infoscience_exports" --role "postgres" --no-password  --disable-triggers --create --clean --exit-on-error --verbose "/media/del/SSD850EVO1TB/workspace/Infoscience-exports-data/backup.sql.tar"
    ```


## Pour tind
on enlève la table public.django_session ->
(à vérifier)

```
postgres sh -c 'exec pg_dump -C -hpostgres -Upostgres -Ox -Ft -T public.django_session \
-f/backup/2020-02-28:14:41:49-0d084e5122051ec5b299c76647609589235e09b6.sql.tar -dinfoscience_exports'
```


