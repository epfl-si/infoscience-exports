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
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['jahia_csv_path'][0], 'w') as csv_jahia_file:
            logger.info("Building jahia csv : {}".format(options['jahia_csv_path'][0]))
            writer = csv.writer(csv_jahia_file)

            for legacy_export in LegacyExport.objects.filter(origin='JAHIA').select_related('export'):
                new_url = settings.SITE_DOMAIN + legacy_export.export.get_absolute_url()
                row = ast.literal_eval(legacy_export.raw_csv_entry)
                row.append(new_url)
                writer.writerow(row)

        with open(options['people_csv_path'][0], 'w') as csv_people_file:
            logger.info(
                "Building people csv : {}".format(options['people_csv_path'][0]))
            writer = csv.writer(csv_people_file)
            writer.writerow(['user', 'addrlog', 'sciper', 'id', 'cvlang', 'src', 'new_url'])

            for legacy_export in LegacyExport.objects.filter(origin='PEOPLE').select_related('export'):
                row = ast.literal_eval(legacy_export.raw_csv_entry)
                row.append(new_url)
                writer.writerow(row)
