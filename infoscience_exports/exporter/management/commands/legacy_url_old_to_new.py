import operator
import ast
import csv
import logging

from functools import reduce
from django.core.management.base import BaseCommand
from django.conf import settings

from exporter.models import SettingsModel
from exports.models import LegacyExport

logger = logging.getLogger('migration')


class Command(BaseCommand):

    help = "Write to csv what become of the old url with the new system \n" \
           "If you provide the ids_csv_path parameters, we build the csv only \n" \
           "on the legacy id list"

    def add_arguments(self, parser):
        parser.add_argument('--ids_csv_path', nargs='+', type=str)
        parser.add_argument('--all_csv_path', nargs='+', type=str)
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        selective_mode = False
        list_ids = []

        if options.get('ids_csv_path'):
            selective_mode = True
            self.stdout.write("Selective mode ON")
        if selective_mode:
            # selective mode
            with open(options['ids_csv_path'][0], 'r') as ids_csv_path:
                reader = csv.reader(ids_csv_path)
                next(reader)
                # from l = [[1,2,3],[4,5,6], [7], [8,9]] to
                # [1, 2, 3, 4, 5, 6, 7, 8, 9]
                list_ids = list(reader)
                list_ids = reduce(operator.concat, list_ids)

        with open(options['jahia_csv_path'][0], 'w') as csv_jahia_file:
            logger.info("Building jahia csv : {}".format(options['jahia_csv_path'][0]))
            writer = csv.writer(csv_jahia_file)

            if selective_mode:
                legacy_exports = LegacyExport.objects.filter(
                    origin='JAHIA').filter(legacy_id__in=list_ids).select_related('export')
            else:
                legacy_exports = LegacyExport.objects.filter(
                    origin='JAHIA').select_related('export')

            for legacy_export in legacy_exports:
                new_url = settings.SITE_DOMAIN + legacy_export.get_with_langage_absolute_url()
                row = ast.literal_eval(legacy_export.raw_csv_entry)
                row.append(new_url)
                writer.writerow(row)

        with open(options['people_csv_path'][0], 'w') as csv_people_file:
            logger.info(
                "Building people csv : {}".format(options['people_csv_path'][0]))
            writer = csv.writer(csv_people_file)
            writer.writerow(['user', 'addrlog', 'sciper', 'id', 'cvlang', 'src', 'new_url'])

            if selective_mode:
                legacy_exports = LegacyExport.objects.filter(
                    origin='PEOPLE').filter(legacy_id__in=list_ids).select_related('export')
            else:
                legacy_exports = LegacyExport.objects.filter(
                    origin='PEOPLE').select_related('export')

            for legacy_export in legacy_exports:
                new_url = settings.SITE_DOMAIN + legacy_export.get_with_langage_absolute_url()
                row = ast.literal_eval(legacy_export.raw_csv_entry)
                row.append(new_url)
                writer.writerow(row)

        if options.get('all_csv_path'):
            with open(options['all_csv_path'][0], 'w') as csv_all_file:
                logger.info(
                    "Building cumul csv : {}".format(options['all_csv_path'][0])
                )
                writer = csv.writer(csv_all_file)
                writer.writerow(
                    ['legacy_id', 'old_url', 'new_url', 'old_key', 'generated_url'])

                if selective_mode:
                    legacy_exports = LegacyExport.objects.filter(
                        legacy_id__in=list_ids).select_related('export')
                else:
                    legacy_exports = LegacyExport.objects.select_related('export')

                for legacy_export in legacy_exports:
                    new_url = settings.SITE_DOMAIN + legacy_export.get_with_langage_absolute_url()
                    # direct access to legacy instead of the infoscience proxy
                    old_url = legacy_export.legacy_url.replace('infoscience.epfl.ch', 'infoscience-legacy.epfl.ch')
                    old_key = 'n/a'
                    try:
                        old_key = SettingsModel.objects.get(id=legacy_export.legacy_id).search_values()
                    except SettingsModel.DoesNotExist:
                        pass

                    new_key = legacy_export.export.url

                    row = [legacy_export.legacy_id, old_url, new_url, old_key, new_key]
                    writer.writerow(row)
