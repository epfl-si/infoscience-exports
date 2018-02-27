#!make
# Default values, can be overridden either on the command line of make
# or in .env

.PHONY: version vars init-venv init-docker init-db test coverage reset deploy release

version:
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py appversion all

vars:
	@echo 'Used by App:'
	@echo '  SECRET_KEY=${SECRET_KEY}'
	@echo '  DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}'
	@echo '  ALLOWED_HOST=${ALLOWED_HOST}'
	@echo '  SITE_URL=${SITE_URL}'
	@echo '  DATABASE_URL=${DATABASE_URL}'
	@echo '  MOCKS_DATABASE_URL=${MOCKS_DATABASE_URL}'
	@echo ''
	@echo 'Used by docker-compose and Nginx'
	@echo '  DEV_PORT=${DEV_PORT}'
	@echo '  ALLOWED_HOST=${ALLOWED_HOST}'
	@echo ''
	@echo 'Used by Makefile'
	@echo '  SUPER_ADMIN_USERNAME=${SUPER_ADMIN_USERNAME}'
	@echo '  SUPER_ADMIN_EMAIL=${SUPER_ADMIN_EMAIL}'
	@echo '  DATABASE_USER=${DATABASE_USER}'
	@echo '  DATABASE_PASSWORD=xxx'
	@echo '  DB_NAME=${DB_NAME}'
	@echo '  MOCKS_DB_NAME=${MOCKS_DB_NAME}'
	@echo ''
	@echo 'Defined as helpers'
	@echo '  DB_URL=${DB_URL}'

init-venv:
ifeq ($(wildcard .env),)
	cp env/django.env .env
	echo SECRET_KEY=`openssl rand -base64 32` >> .env
	echo PYTHONPATH=`pwd`/infoscience_exports >> .env
	@echo "! Set up your .env file before running"
endif
	@echo "! If you want a clean state from a docker standpoint, run"
	@echo "!   $$ make init-docker"

build:
	# udpating requirements
	pipenv lock --requirements > requirements.txt
	echo "-r requirements.txt" > requirements-dev.txt
	pipenv lock --requirements --dev >> requirements-dev.txt
	# clean up requirements	
	sed -i "s/# -e git/-e git/g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements-dev.txt
	# collectstatic
	python infoscience_exports/manage.py collectstatic
	# build docker image
	docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml build

init-docker: build
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
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py test exports --noinput --failfast --keepdb

coverage: check-env
	flake8 infoscience_exports/exports --max-line-length=120
	docker-compose -f docker-compose-dev.yml exec web infoscience_exports/manage.py test exports --noinput
	coverage html
	open htmlcov/index.html

reset: 
	make init-docker
	@echo ''
	@echo "! sleeping 3secs, time for postgres container to be available"
	@echo ''
	make init-db

restart:
	docker-compose -f docker-compose-dev.yml restart web

dump:
	@echo dumping DB on last commit `git rev-parse --verify HEAD`
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_dump -C -hpostgres -Upostgres -Ox -Ft \
		   -f/backup/$(shell date +"%F:%T")-$(shell git rev-parse --verify HEAD).sql.tar -d${DB_NAME}'

restore:
	@echo restoring DB from file `ls -t backup/*.sql.tar | head -1`
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_restore -c -hpostgres -U${DATABASE_USER} -Ox -Ft -d${DB_NAME} `ls -t /backup/*.sql.tar | head -1`'
	make restart

release:
	# updating CHANGELOG
	github_changelog_generator
	# confirm version number
	# see https://stackoverflow.com/questions/39272954/how-to-prompt-user-for-y-n-in-my-makefile-with-pure-make-syntaxis
	# docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py appversion version
	# commit master

	# git tag ADD-$-TO-(sell command) (shell docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py appversion version)
	# git push --tags
	# git checkout release
	# git merge master

deploy: dump
	docker-compose -f docker-compose-dev.yml build web
	make restart
	@echo ''
	@echo "Deployment done with following commit:"
	git log -n 1

check-env:
ifeq ($(wildcard .env),)
	@echo "Please create your .env file first, from .env.sample or by running make venv"
	@exit 1
else
include .env
export
endif
