#!make
# Default values, can be overridden either on the command line of make
# or in .env

.PHONY: init-venv init-docker init-db vars test coverage reset deploy

vars:
	@echo 'App-related vars:'
	@echo '  SECRET_KEY=${SECRET_KEY}'
	@echo '  DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}'
	@echo '  SITE_URL=${SITE_URL}'
	@echo '  ALLOWED_HOST=${ALLOWED_HOST}'
	@echo '  DATABASE_URL=${DATABASE_URL}'
	@echo '  MOCKS_DATABASE_URL=${MOCKS_DATABASE_URL}'
	@echo ''
	@echo 'Dev-related vars:'
	@echo '  DEV_PORT=${DEV_PORT}'

init-venv:
ifeq ($(wildcard .env),)
	cp env/django.env .env
	echo SECRET_KEY=`openssl rand -base64 32` >> .env
	echo PYTHONPATH=`pwd`/infoscience_exports >> .env
	@echo "! Set up your .env file before running"
endif
	@echo "! If you want a clean state from a docker standpoint, run"
	@echo "!   $$ make init-docker"

init-docker:
	docker-compose -f docker-compose-dev.yml down
	docker system prune
	docker-compose -f docker-compose-dev.yml build
	docker-compose -f docker-compose-dev.yml up -d
	docker-compose -f docker-compose-dev.yml logs

init-db:
	# create DB
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql -c 'CREATE DATABASE "${DB_NAME}";' -U postgres
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql -c 'CREATE DATABASE "${MOCKS_DB_NAME}";' -U postgres
	# create DB user for app
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "CREATE USER ${DATABASE_USER} WITH PASSWORD '${DATABASE_PASSWORD}';" -U postgres
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "ALTER ROLE ${DATABASE_USER} WITH CREATEDB;" -U postgres
	# initialize DBs executing migration scripts
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py migrate
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py migrate --database=mock
	# create super admin in app
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py createsuperuser --username=${SUPER_ADMIN_USERNAME} --email=${SUPER_ADMIN_EMAIL} --noinput
	@echo "  -> All set up! You can connect with your tequilla acount or the admin (${SUPER_ADMIN_EMAIL})"

test: check-env
	flake8 infoscience_exports/exports --max-line-length=120
	pytest --cov=infoscience_exports/exports infoscience_exports/exports/test

coverage: test
	coverage html
	open htmlcov/index.html

reset: 
	make init-docker
	@echo "sleeping 3secs, time for postgres container to be available"
	make init-db

deploy:
	docker-compose -f docker-compose-dev.yml stop web
	docker-compose -f docker-compose-dev.yml build web
	docker-compose -f docker-compose-dev.yml run -d web

check-env:
ifeq ($(wildcard .env),)
	@echo "Please create your .env file first, from .env.sample or by running make venv"
	@exit 1
else
include .env
export
endif
