#!make
# Default values, can be overridden either on the command line of make
# or in .env

.PHONY: init-venv init-heroku init-docker init-db vars coverage run gunicorn local deploy

vars:
	@echo 'App-related vars:'
	@echo '  SECRET_KEY=${SECRET_KEY}'
	@echo '  DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}'
	@echo '  SITE_URL=${SITE_URL}'
	@echo '  DATABASE_URL=${DATABASE_URL}'
	@echo '  MOCKS_DATABASE_URL=${MOCKS_DATABASE_URL}'
	@echo ''
	@echo 'Dev-related vars:'
	@echo '  DEV_PORT=${DEV_PORT}'
	@echo '  DEV_DB_HOST=${DEV_DB_HOST}'
	@echo '  DEV_DB_PORT=${DEV_DB_PORT}'
	@echo '  DEV_DATABASE_URL=${DEV_DATABASE_URL}'
	@echo '  DEV_MOCKS_DATABASE_URL=${DEV_MOCKS_DATABASE_URL}'
	@echo ''
	@echo 'Heroku-related vars:'
	@echo '  HEROKU_APP=${HEROKU_APP}'
	@echo '  HEROKU_URL=${HEROKU_URL}'
	@echo '  HEROKU_GIT=${HEROKU_GIT}'
	@echo '  DB_URI_VAR_NAME=${DB_URI_VAR_NAME}'
	@echo '  HEROKU_USERNAME=${HEROKU_USERNAME}'
	@echo '  HEROKU_PASSWORD=xxx'

init-venv:
ifeq ($(wildcard .env),)
	cp env/django.env .env
	echo PYTHONPATH=`pwd`/infoscience_exports >> .env
	SECRET=`openssl rand -base64 32` sed -i s/your-secret/${SECRET}/g .env
endif
	pipenv --update 
	pipenv update --dev --python 3
	@echo "! Set up your .env file before running"
	@echo "!   $$ make init-heroku"
	@echo "! If you want a clean state from a docker standpoint, run"
	@echo "!   $$ make init-docker"

init-heroku:
	heroku create ${HEROKU_APP} || true
	heroku config:set PYTHONPATH="./infoscience_exports"
	heroku config:set SECRET_KEY="${SECRET_KEY}"
	heroku config:set MAIL_USERNAME="${HEROKU_USERNAME}"
	@heroku config:set MAIL_PASSWORD="${HEROKU_PASSWORD}" > /dev/null
	heroku addons:add heroku-postgresql:hobby-dev
	heroku addons:add heroku-postgresql:hobby-dev
	@echo "  -> Replace HEROKU_APP vars in your .env file"
	@echo "  -> Run 'heroku run init' when done"

init-docker:
	docker-compose -f docker-compose-dev.yml down
	docker system prune
	docker-compose -f docker-compose-dev.yml build
	docker-compose -f docker-compose-dev.yml up -d
	docker-compose -f docker-compose-dev.yml logs

restart-docker:
	docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml up -d

init-db:
	@echo "! init-db needs a clean DB... if you wantwork locally, run :"
	@echo "!   $$ make init-docker"
	@echo "! first in order to clean docker volumes"
	# create DB
	psql ${DEV_DB_URL} -c 'CREATE DATABASE "${DB_NAME}";' -U postgres
	psql ${DEV_DB_URL} -c 'CREATE DATABASE "${MOCKS_DB_NAME}";' -U postgres
	# create DB user for app
	psql ${DEV_DATABASE_URL} -c "CREATE USER ${DATABASE_USER} WITH PASSWORD '${DATABASE_PASSWORD}';" -U postgres
	psql ${DEV_DATABASE_URL} -c "ALTER ROLE ${DATABASE_USER} WITH CREATEDB;" -U postgres
	# initialize DBs executing migration scripts
	DATABASE_URL=postgres://${DATABASE_USER}:${DATABASE_PASSWORD}@${DEV_DB_HOST}:${DEV_DB_PORT}/${DB_NAME} \
		python infoscience_exports/manage.py migrate
	MOCKS_DATABASE_URL=postgres://${DATABASE_USER}:${DATABASE_PASSWORD}@${DEV_DB_HOST}:${DEV_DB_PORT}/${MOCKS_DB_NAME} \
		python infoscience_exports/manage.py migrate --database=mock
	# create super admin in app
	DATABASE_URL=postgres://${DATABASE_USER}:${DATABASE_PASSWORD}@${DEV_DB_HOST}:${DEV_DB_PORT}/${DB_NAME} \
		python infoscience_exports/manage.py createsuperuser --username=${SUPER_ADMIN_USERNAME} --email=${SUPER_ADMIN_EMAIL} --noinput
	@echo "  -> All set up! You can connect with your tequilla acount or the admin (${SUPER_ADMIN_EMAIL})"

info:
	heroku apps
	heroku addons
	heroku config

test: check-env
	flake8 infoscience_exports/exports --max-line-length=120
	pytest --cov=infoscience_exports/exports infoscience_exports/exports/test

coverage: test
	coverage html
	open htmlcov/index.html

heroku: test
	@echo "! heroku makes use of DB... if you want to start from sratch, run :"
	@echo "!   $$ make init-docker"
	@echo "!   $$ make init-db"
	docker-compose -f docker-compose-dev.yml start postgres
	DATABASE_URL=${DEV_DATABASE_URL} heroku local -p 7000

deploy: test
	git push heroku master

check-env:
ifeq ($(wildcard .env),)
	@echo "Please create your .env file first, from .env.sample or by running make venv"
	@exit 1
else
include .env
export
endif
