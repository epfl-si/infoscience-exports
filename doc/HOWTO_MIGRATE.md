# Migration steps

## Pre

Assert that you can put files in infoscience_exports/exporter/fixtures and that folder is a volume to /usr/src/app/infoscience_exports/exporter/fixtures/

Files that should be in this folder:

* exports_from_32.json
  * the dump from the old export system
* infoscience-people-actif-only.csv.extended.csv
  * the list of exports from people.epfl.ch with their sciper, username and email
* infoscience-prod-jahia.csv.extended.csv
  * the list of exports from our CMS;  with their sciper, username and email

## Do

1. `make migration-load-dump`
  * nothing fancy here, only the load of json values to an empty SettingsModel table

2.a `make migration-migrate`
  * one-shot migration that will create exports for Jahia and People (~4000)
  * see /var/log/django/infoscience_exports_migration.log

2.b `docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py migrate_from_legacy --urls_csv_path ./infoscience_exports/exporter/fixtures/urls_to_migrate.csv`

  * selective migration for only the urls provided
  * put your csv of the urls from legacy to migrate in entry

## Post

1. `make migration-post-generate-csv`
  * this will create two files in /var/log/django
    * /var/log/django/infoscience_exports_new_url_jahia.csv
    * /var/log/django/infoscience_exports_new_url_people.csv
  * this can be run as many times as needed
