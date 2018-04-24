import csv
import operator

from functools import reduce

from django.core.management.base import BaseCommand

from exporter.models import SettingsModel

"""
dump with 
    manage.py dumpdata -o ./exports_from_32.json exporter

load dump with
    make migration-load-dump

do the migration with
    make migration-migrate
"""


class Command(BaseCommand):

    help = "Migrate exports from infoscience-legacy base to the new format"

    def add_arguments(self, parser):
        parser.add_argument('--urls_csv_path', nargs='+', type=str)
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        list_urls = []

        if options.get('urls_csv_path'):
            with open(options['urls_csv_path'][0], 'r') as urls_csv_file:
                # from l = [[1,2,3],[4,5,6], [7], [8,9]] to
                # [1, 2, 3, 4, 5, 6, 7, 8, 9]
                reader = csv.reader(urls_csv_file)
                next(reader)
                urls_csv_list = list(reader)
                list_urls = reduce(operator.concat, urls_csv_list)

        SettingsModel.objects.load_exports_from_jahia(
            options['jahia_csv_path'][0],
            list_urls)
        SettingsModel.objects.load_exports_from_people(
            options['people_csv_path'][0],
            list_urls)
