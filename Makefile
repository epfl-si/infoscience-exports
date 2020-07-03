#!make
# Default values, can be overridden either on the command line of make
# or in .env

.PHONY: version vars init-venv build build-travis init-db reset \
	up down logs restart restart-web \
	superadmin collectstatic migrations migrate \
	dump restore release push-prod deploy \
	fast-test test test-render stop coverage shell bash \
	migration-load-dump migration-build-delta \
	migration-post-generate-csvs migration-migrate \
	migration-migrate-selective-with-subset migration-migrate-all \
	migration-post-generate-csv-all setup-openshift

VERSION:=$(shell python update_release.py -v)

version:
	@echo VERSION set to $(VERSION)

vars:
	@echo 'Used by App:'
	@echo '  SECRET_KEY=${SECRET_KEY}'
	@echo '  DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}'
	@echo '  SERVER_HOST=${SERVER_HOST}'
	@echo '  DEV_PORT=${DEV_PORT}'
	@echo '  SITE_PATH=${SITE_PATH}'
	@echo '  SITE_URL=${SITE_URL}'
	@echo '  ALLOWED_HOSTS=${ALLOWED_HOSTS}'
	@echo '  DATABASE_URL=${DATABASE_URL}'
	@echo ''
	@echo 'Used by Makefile'
	@echo '  SUPER_ADMIN_USERNAME=${SUPER_ADMIN_USERNAME}'
	@echo '  SUPER_ADMIN_EMAIL=${SUPER_ADMIN_EMAIL}'
	@echo '  GITHUB_OWNER=${GITHUB_OWNER}'
	@echo '  GITHUB_REPO=${GITHUB_REPO}'
	@echo '  GITHUB_USER=${GITHUB_USER}'
	@echo '  GITHUB_KEY=${GITHUB_KEY}'
	@echo '  DATABASE_USER=${DATABASE_USER}'
	@echo '  DATABASE_PASSWORD=xxx'
	@echo '  DB_NAME=${DB_NAME}'
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
	@echo "!   $$ make reset"

build:
	# udpating requirements
	pipenv lock --requirements > requirements.txt
	echo "-r requirements.txt" > requirements-dev.txt
	pipenv lock --requirements --dev >> requirements-dev.txt
	# clean up requirements
	sed -i "s/# -e git/-e git/g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements-dev.txt
	# build docker image
	docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml build

init-db:
	# create DB
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql -c 'CREATE DATABASE "${DB_NAME}";' -U postgres
	# create DB user for app
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "CREATE USER ${DATABASE_USER} WITH PASSWORD '${DATABASE_PASSWORD}';" -U postgres
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "ALTER ROLE ${DATABASE_USER} WITH CREATEDB;" -U postgres
	# initialize DBs executing migration scripts
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py makemigrations
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py migrate
	# make a room for the cache
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py createcachetable
	# create super admin in app
	make superadmin
	@echo "  -> All set up! You can connect with your tequila acount or the admin (${SUPER_ADMIN_EMAIL})"

reset: build up
	@echo ''
	@echo "! sleeping 6secs, time for postgres container to be available"
	@echo ''
	sleep 6
	make init-db
	make collectstatic
	make compilemessages

up:
	docker-compose -f docker-compose-dev.yml up -d

stop:
	docker-compose -f docker-compose-dev.yml stop

down:
	docker-compose -f docker-compose-dev.yml down

logs:
	docker-compose -f docker-compose-dev.yml logs -f

restart:
	# FIXME: OperationalError at / FATAL: role "django" does not exist
	# docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml up -d
	docker-compose -f docker-compose-dev.yml logs

restart-web:
	docker-compose -f docker-compose-dev.yml stop web
	docker-compose -f docker-compose-dev.yml start web

superadmin:
	docker-compose -f docker-compose-dev.yml exec web \
	python infoscience_exports/manage.py shell -c "from django.contrib.auth import get_user_model; \
		User = get_user_model(); \
		User.objects.filter(email='${SUPER_ADMIN_EMAIL}').delete(); \
		User.objects.create_superuser('${SUPER_ADMIN_USERNAME}', '${SUPER_ADMIN_EMAIL}', '${SUPER_ADMIN_PASSWORD}');"

collectstatic: up
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py collectstatic --noinput

migrations: up
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py makemigrations

migrate: up
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py migrate

messages: up
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py makemessages --all

compilemessages: up
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py compilemessages

dump:
	@echo dumping DB on last commit `git rev-parse --verify HEAD`
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_dump -C -hpostgres -Upostgres -Ox -Ft \
		   -f/backup/$(shell date +"%F:%T")-$(shell git rev-parse --verify HEAD).sql.tar -d${DB_NAME}'

restore:
	@echo restoring DB from file `ls -t backup/*.sql.tar | head -1`
	# retrieve commit number and checkout
	git checkout $(shell ls -t backup/*.sql.tar | head -1 | cut -d'-' -f4 | cut -d '.' -f1)

	# restore DB
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_restore -c -hpostgres -U${DATABASE_USER} -Ox -Ft -d${DB_NAME} `ls -t /backup/*.sql.tar | head -1`'

	# restart web container
	make restart-web

release:
	# make sure we are in master
	python update_release.py check --branch=master

	# update versions and ask for confirmation
	python update_release.py
	python update_release.py confirm

	# create branch and tag
	git checkout -b release-$(VERSION)
	git add .
	git commit -m "Prepared release $(VERSION)"
	git push --set-upstream origin release-$(VERSION)

	git tag $(VERSION)
	git tag -f qa-release
	git push --tags --force

	# updating CHANGELOG
	make update-changelog

	# create github release
	python update_release.py publish

	# cancel pre-update of versions
	git checkout infoscience_exports/exports/versions.py

	# git merge master
	git checkout master
	git merge release-$(VERSION)
	git push

push-qa:
	# update tags
	git tag -f qa-release
	git push --tags --force

	# updating CHANGELOG
	make update-changelog

push-prod:
	@# confirm push to production
	@python update_release.py confirm --prod

	# update tags
	git tag -f prod-release
	git push --tags --force

	# updating CHANGELOG
	make update-changelog

update-changelog:
	# updating CHANGELOG
	github_changelog_generator

	# commit master
	git add CHANGELOG.md
	git commit -m "updated CHANGELOG"
	git push

deploy: dump
	git pull
	# update docker images
	docker-compose -f docker-compose-dev.yml build
	# restart containers
	make restart
	# update DB
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py migrate
	# update languages
	make collectstatic
	make compilemessages
	# restart web container
	make restart-web

fast-test: check-env
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py test exports --settings=settings.test --noinput --failfast --keepdb

test: check-env
	docker-compose -f docker-compose-dev.yml exec web \
		flake8 infoscience_exports/exports --max-line-length=120 --exclude=migrations
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py test exports --settings=settings.test --noinput

test-render: check-env
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py test --failfast exports.test.test_crud_views:ExportRenderTest --settings=settings.test-silent-coverage --noinput

shell:
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py shell_plus

bash:
	docker-compose -f docker-compose-dev.yml exec web \
		bash

coverage: check-env
	flake8 infoscience_exports/exports --max-line-length=120 --exclude=migrations
	pytest --cov=infoscience_exports infoscience_exports/exports/pytests
	coverage html
	open htmlcov/index.html

build-travis:
	docker-compose -f docker-compose-dev.yml build
	docker-compose -f docker-compose-dev.yml up -d

test-travis:
	flake8 infoscience_exports/exports --max-line-length=120 --exclude=migrations
	python infoscience_exports/manage.py test exports --settings=settings.test --noinput
	coverage xml

migration-load-dump:
	docker-compose -f docker-compose-dev.yml exec web \
		python infoscience_exports/manage.py loaddata --app exporter exports_from_32

migration-build-delta:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py add_quality_content_comparaison

migration-migrate:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py \
	migrate_from_legacy --jahia_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-prod-jahia.csv.extended.csv \
            --people_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-people-actif-only.csv.extended.csv \
            --ids_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/ids_to_migrate.csv

migration-migrate-selective-with-subset:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py \
	migrate_from_legacy --jahia_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-prod-jahia.csv.extended.csv \
            --people_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-people-actif-only.csv.extended.csv \
            --ids_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/ids_to_migrate.csv \
            --subset_only 1

migration-migrate-all:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py \
	migrate_from_legacy --jahia_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-prod-jahia.csv.extended.csv \
            --people_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-people-actif-only.csv.extended.csv \
            --migrate_all 1

migration-post-generate-csv:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py legacy_url_old_to_new \
	--ids_csv_path "/usr/src/app/infoscience_exports/exporter/fixtures/ids_to_migrate.csv" \
	--jahia_csv_path "/var/log/django/infoscience_exports_new_url_jahia.csv" \
	--people_csv_path "/var/log/django/infoscience_exports_new_url_people.csv " \
	--all_csv_path "/var/log/django/infoscience_exports_all_new_url.csv"

migration-post-generate-csv-all:
	docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py legacy_url_old_to_new \
	--jahia_csv_path "/var/log/django/infoscience_exports_new_url_jahia.csv" \
	--people_csv_path "/var/log/django/infoscience_exports_new_url_people.csv " \
	--all_csv_path "/var/log/django/infoscience_exports_all_new_url.csv"

setup-openshift:check-env
	./ansible/exportsible

check-env:
ifeq ($(wildcard .env),)
	@echo "Please create your .env file first, from .env.sample or by running make venv"
	@exit 1
else
include .env
export
endif
