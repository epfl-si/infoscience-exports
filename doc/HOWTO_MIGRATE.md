# Migration steps

## Pre-requisites

Assert that the listed files are accessible from inside the container.
In this document, the assumption is made that the path is `/usr/src/app/infoscience_exports/exporter/fixtures/`

The files can be found on Google Drive

Files that should be in this folder before running any command :

* exports_from_32.json
  * the dump from the old export system

* infoscience-people-actif-only.csv.extended.csv
  * the list of exports from people.epfl.ch with their sciper, username and email

* infoscience-prod-jahia.csv.extended.csv
  * the list of exports from our CMS;  with their sciper, username and email

* ids_to_migrate.csv
  * the legacy export ids that we need to migrate


### Pre-step, only one time

1. Inside the container, run : `python infoscience_exports/manage.py loaddata --app exporter exports_from_32`
  * nothing fancy here, only the load of json values to an empty SettingsModel table
  * once it's done, you should never need to rerun again as the data will not evolve


## Do the migration
1. Inside the container, run :

```
python infoscience_exports/manage.py migrate_from_legacy \
--ids_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/ids_to_migrate.csv \
--people_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-people-actif-only.csv.extended.csv \
--jahia_csv_path /usr/src/app/infoscience_exports/exporter/fixtures/infoscience-prod-jahia.csv.extended.csv
```

## After the migration

1. Inside the container, run :

```
python infoscience_exports/manage.py legacy_url_old_to_new \
    --jahia_csv_path /var/log/django/infoscience_exports_new_url_jahia.csv \
    --people_csv_path /var/log/django/infoscience_exports_new_url_people.csv
```

## Files to upload after a migration

On the Google Drive folder, put this files in the subfolder `2018-04-xx raw files`

* /var/log/django/infoscience_exports_new_url_jahia.csv
* /var/log/django/infoscience_exports_new_url_people.csv
* /var/log/django/infoscience_exports_migration.log
