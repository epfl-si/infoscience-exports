import csv, re
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError

from exporter.models import SettingsModel


class Command(BaseCommand):

    help = "For export found in jahia or people, add them as new exports" \
           "people list exports-sciper (provided by Ion)" \
           "jahia list of exports-sciper (provided by Francis, INC0219923)"

    def add_arguments(self, parser):
        parser.add_argument('--output_csv_path', nargs='*', type=str)
        parser.add_argument('--people_csv_path', nargs='*', type=str)
        parser.add_argument('--jahia_csv_path', nargs='*', type=str)

    def handle(self, output_csv_path, people_csv_path, jahia_csv_path, *args, **options):
        if not output_csv_path:
            raise CommandError("Missing the 'output_csv_path' argument")
        if not people_csv_path:
            raise CommandError("Missing the 'people_csv_path' argument")
        if not jahia_csv_path:
            raise CommandError("Missing the 'jahia_csv_path' argument")

        with open(jahia_csv_path[0], 'r') as f:
            reader = csv.reader(f)
            jahia_full_list = list(reader)
            jahia_legacy_exports_ids = []

            for row in jahia_full_list[1:]:
                jahia_legacy_exports_id = SettingsModel.objects.get_legacy_export_id_from_url(row[8])
                if jahia_legacy_exports_id:
                    jahia_legacy_exports_ids.append(jahia_legacy_exports_id)

            self.stdout.write("Jahia ids found {}".format(jahia_legacy_exports_ids))

        with open(people_csv_path[0], 'r') as f:
            reader = csv.reader(f)
            people_full_list = list(reader)
            people_legacy_exports_ids = []

            for row in people_full_list[1:]:
                people_legacy_exports_id = SettingsModel.objects.get_legacy_export_id_from_url(row[2].strip())
                if people_legacy_exports_id:
                    people_legacy_exports_ids.append(people_legacy_exports_id)
            self.stdout.write(
                "People ids found {}".format(people_legacy_exports_ids))

        with open(output_csv_path[0], 'w') as f:
            writer = csv.writer(f)

            writer.writerow(['legacy id',
                             'legacy url',
                             'new generated url',
                             'number of new elements since migration',
                             'used in',
                             ])

            i = 0
            total = SettingsModel.objects.count()

            for exporter in SettingsModel.objects.all():
                i = i+1
                self.stdout.write("Doing n. {}/{}".format(i, total))

                used_in = ''

                if str(exporter.id) in jahia_legacy_exports_ids:
                    used_in = 'Jahia'
                elif str(exporter.id) in people_legacy_exports_ids:
                    used_in = 'People'
                else:
                    #ignore
                    self.stdout.write("Can not found an usage for this url")
                    continue

                old_url = 'https://infoscience-legacy.epfl.ch/' \
                          'curator/export/{}'.format(exporter.id)

                try:
                    invenio_vars = {
                        'd1d': '29',
                        'd1m': '01',
                        'd1y': '2018',
                        'of' : 'xm',
                    }
                    new_url = exporter.build_advanced_search_url(invenio_vars=invenio_vars)
                except ValueError:
                    self.stdout.write("ignoring this basket url")
                    continue

                infoscience_to_read = urlopen(new_url)
                infoscience_read = infoscience_to_read.read().decode('utf-8')
                infoscience_to_read.close()

                text_to_find = r"<!-- Search-Engine-Total-Number-Of-Results: (\d+)"
                m = re.search(text_to_find, infoscience_read)

                number_of_new_record = 0

                if not m:
                    # we found nothing, skip this
                    self.stdout.write("Look like there is no new record, end here")
                    continue

                if m.group(1):
                    number_of_new_record = m.group(1)

                row = [
                    exporter.id,
                    old_url,
                    new_url,
                    number_of_new_record,
                    used_in,
                ]

                writer.writerow(row)
