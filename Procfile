web: gunicorn --reload -w 4 -b :80 --chdir ./infoscience_exports wsgi:application

create-user: psql $DATABASE_URL -c "CREATE USER django WITH PASSWORD '$DATABASE_PASSWORD';"
grant-user: psql $DATABASE_URL -c "ALTER ROLE django WITH CREATEDB;"
init-db: python infoscience_exports/manage.py migrate
init-mocks: python infoscience_exports/manage.py migrate --database=mock
