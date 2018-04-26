import csv, re
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError

from exporter.models import SettingsModel
from exports.models import LegacyExport


class Command(BaseCommand):

    help = "Check on migrated export if we have new publications on prod."

    def add_arguments(self, parser):
        parser.add_argument('--output_csv_path', nargs='*', type=str)

    def handle(self, output_csv_path, *args, **options):
        if not output_csv_path:
            raise CommandError("Missing the 'output_csv_path' argument")

        with open(output_csv_path[0], 'w') as f:
            writer = csv.writer(f)

            writer.writerow(['legacy id',
                             'legacy url',
                             'new generated url',
                             'url for counting',
                             'number of new elements since migration',
                             'used in',
                             ])

            i = 0
            total = LegacyExport.objects.count()

            invenio_vars = {
                'd1d': '29',
                'd1m': '01',
                'd1y': '2018',
                'of': 'xm'
            }

            for legacy_export in LegacyExport.objects.all().select_related('export'):
                i = i + 1
                self.stdout.write("Doing n. {}/{}".format(i, total))

                old_settings = SettingsModel.objects.get(id=legacy_export.legacy_id)
                number_of_new_record = 0
                try:
                    count_url = old_settings.build_advanced_search_url(invenio_vars=invenio_vars)
                    infoscience_to_read = urlopen(count_url)
                    infoscience_read = infoscience_to_read.read().decode('utf-8')
                    infoscience_to_read.close()

                    text_to_find = r"<!-- Search-Engine-Total-Number-Of-Results: (\d+)"
                    m = re.search(text_to_find, infoscience_read)

                    if m and m.group(1):
                        number_of_new_record = m.group(1)
                except ValueError:
                    # it's a basket, ignore
                    count_url = ''
                    number_of_new_record = 'n/a'

                row = [
                    legacy_export.legacy_id,
                    legacy_export.legacy_url,
                    legacy_export.export.url,
                    count_url,
                    number_of_new_record,
                    legacy_export.origin,
                ]

                writer.writerow(row)
