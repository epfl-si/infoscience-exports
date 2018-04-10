import csv, re
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError

from exporter.models import SettingsModel


class Command(BaseCommand):

    help = "For export found in jahia or people, add them as new exports" \
           "people list exports-sciper (provided by Ion)" \
           "jahia list of exports-sciper (provided by Francis, INC0219923)"

    def add_arguments(self, parser):
        parser.add_argument('output', nargs='*', type=str)
        parser.add_argument('people', nargs='*', type=str)
        parser.add_argument('jahia', nargs='*', type=str)

    def handle(self, output, people, jahia, *args, **options):
        if not output:
            raise CommandError("Missing the 'output' argument")
        if not people:
            raise CommandError("Missing the 'people' argument")
        if not jahia:
            raise CommandError("Missing the 'jahia' argument")

        with open(output[0], 'w') as f:
            writer = csv.writer(f)

            writer.writerow(['legacy id',
                             'legacy url',
                             'new generated url',
                             'number of new elements since migration',
                             ])

            i = 0
            total = SettingsModel.objects.count()

            for exporter in SettingsModel.objects.all():
                i = i+1
                self.stdout.write("Doing n. {}/{}".format(i, total))
                old_url = 'https://infoscience-legacy.epfl.ch/' \
                          'curator/export/{}'.format(exporter.id)

                try:
                    invenio_vars = {
                        'd1d': '29',
                        'd1m': '01',
                        'd1y': '2018',
                        'of' : 'xm',
                    }
                    new_url = exporter.build_advanced_search_url(invenio_vars=invenio_vars, limit=200)
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
                ]

                writer.writerow(row)
