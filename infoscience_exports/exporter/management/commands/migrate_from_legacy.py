import csv
import operator

from functools import reduce
import logging

from django.core.management.base import BaseCommand, CommandError

from exporter.models import SettingsModel

logger = logging.getLogger('migration')

"""
dump with 
    manage.py dumpdata -o ./exports_from_32.json exporter

load dump with
    make migration-load-dump

do the migration with the provided ids list
    make migration-migrate
"""


class Command(BaseCommand):

    help = "Migrate exports from infoscience-legacy base to the new format\n" \
           "Set --ids_csv_path if you want to limit the scope to a list of id\n" \
           "Set --subset_only if you want to run only the one that we can handle\n" \
           "Set --migrate_all if you want a full migrate without limit"

    def add_arguments(self, parser):
        parser.add_argument('--ids_csv_path', nargs='+', type=str)
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)
        parser.add_argument('--subset_only', nargs='+', type=str)
        parser.add_argument('--migrate_all', nargs='+', type=str)

    def handle(self, *args, **options):
        selective_mode = False
        list_ids = []

        subset_mode = False

        if not options.get('ids_csv_path') and not options.get('subset_only') and not options.get('migate_all'):
            raise CommandError("Set at least --migrate_all if you want a full migration")

        if options.get('ids_csv_path'):
            selective_mode = True
            self.stdout.write("Selective mode ON")

        if options.get('subset_only'):
            subset_mode = True
            self.stdout.write("Subset only ON")

        if selective_mode:
            # selective mode
            with open(options['ids_csv_path'][0], 'r') as ids_csv_path:
                reader = csv.reader(ids_csv_path)
                next(reader)
                # from l = [[1,2,3],[4,5,6], [7], [8,9]] to
                # [1, 2, 3, 4, 5, 6, 7, 8, 9]
                list_ids = list(reader)
                list_ids = reduce(operator.concat, list_ids)

        SettingsModel.objects.load_exports_from_jahia(
            options['jahia_csv_path'][0],
            list_ids,
            subset_mode)
        SettingsModel.objects.load_exports_from_people(
            options['people_csv_path'][0],
            list_ids,
            subset_mode)
