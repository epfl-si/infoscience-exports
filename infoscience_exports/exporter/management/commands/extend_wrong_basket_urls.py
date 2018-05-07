import csv

from django.core.management.base import BaseCommand, CommandError

from exporter.utils import flatten_list
from exports.models import LegacyExport


class Command(BaseCommand):

    help = "Load a csv of legacy_id that need to be extended with debug key"

    def add_arguments(self, parser):
        parser.add_argument('--basket_to_extend_ids_path', nargs='*', type=str)

    def handle(self, *args, **options):
        if not options.get('basket_to_extend_ids_path'):
            raise CommandError

        with open(options['basket_to_extend_ids_path'][0], 'r') as ids_csv_path:
            reader = csv.reader(ids_csv_path)
            next(reader)
            # from l = [[1,2,3],[4,5,6], [7], [8,9]] to
            # [1, 2, 3, 4, 5, 6, 7, 8, 9]
            list_ids = flatten_list(list(reader))

            legacy_exports_to_extend = LegacyExport.objects.filter(legacy_id__in=list_ids).select_related('export')

            for legacy_export in legacy_exports_to_extend:
                export = legacy_export.export
                if export.url and export.url.find('&p=year%3A1111+AND+year%3A9999') == -1:
                    old_url = export.url
                    export.url += '&p=year%3A1111+AND+year%3A9999'
                    new_url = export.url
                    export.save()
                    self.stdout.write("Set from {} to {}".format(old_url, new_url))
