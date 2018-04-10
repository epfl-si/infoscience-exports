from django.core.management.base import BaseCommand

from exporter.models import SettingsModel

"""
dump with 
manage.py dumpdata -o ./exports_from_32.json exporter

load with
make migrate-load-dump
"""


class Command(BaseCommand):

    help = "Migrate exports from infoscience-legacy base to the new format"

    def handle(self, *args, **options):
        # TODO: make it better?
        SettingsModel.objects.load_exports_from_jahia('/usr/src/app/infoscience_exports/exporter/fixtures/infoscience-prod-jahia.csv.extended.csv')
        SettingsModel.objects.load_exports_from_people('/usr/src/app/infoscience_exports/exporter/fixtures/infoscience-people-actif-only.csv.extended.csv')
