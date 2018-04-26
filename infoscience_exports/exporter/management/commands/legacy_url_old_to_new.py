import ast
import csv
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from exports.models import LegacyExport

logger = logging.getLogger('migration')


class Command(BaseCommand):

    help = "Write to csv what become of the old url with the new system "

    def add_arguments(self, parser):
        parser.add_argument('--all_csv_path', nargs='+', type=str)
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['jahia_csv_path'][0], 'w') as csv_jahia_file:
            logger.info("Building jahia csv : {}".format(options['jahia_csv_path'][0]))
            writer = csv.writer(csv_jahia_file)

            for legacy_export in LegacyExport.objects.filter(origin='JAHIA').select_related('export'):
                new_url = settings.SITE_DOMAIN + legacy_export.get_with_langage_absolute_url()
                row = ast.literal_eval(legacy_export.raw_csv_entry)
                row.append(new_url)
                writer.writerow(row)

        with open(options['people_csv_path'][0], 'w') as csv_people_file:
            logger.info(
                "Building people csv : {}".format(options['people_csv_path'][0]))
            writer = csv.writer(csv_people_file)
            writer.writerow(['user', 'addrlog', 'sciper', 'id', 'cvlang', 'src', 'new_url'])

            for legacy_export in LegacyExport.objects.filter(origin='PEOPLE').select_related('export'):
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
                    ['legacy_id', 'old_url', 'new_url'])

                for legacy_export in LegacyExport.objects.select_related('export'):
                    new_url = settings.SITE_DOMAIN + legacy_export.get_with_langage_absolute_url()
                    # direct access to legacy instead of the infoscience proxy
                    old_url = legacy_export.legacy_url.replace('infoscience.epfl.ch', 'infoscience-legacy.epfl.ch')
                    row = [legacy_export.legacy_id, old_url, new_url]
                    writer.writerow(row)
