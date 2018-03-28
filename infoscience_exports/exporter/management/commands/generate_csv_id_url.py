import csv

from django.core.management.base import BaseCommand, CommandError

from exporter.models import SettingsModel


class Command(BaseCommand):

    help = "Generate a csv file, with the exporter id and the url rebuilded"

    def add_arguments(self, parser):
        parser.add_argument('output', nargs='*', type=str)

    # A command must define handle()
    def handle(self, output, *args, **options):
        if not output:
            raise CommandError("Missing the 'output' argument")

        with open(output[0], 'w') as f:
            writer = csv.writer(f)

            writer.writerow(('legacy url', 'new generated url'))

            for exporter in SettingsModel.objects.all():
                old_url = 'https://infoscience-legacy.epfl.ch/curator/export/{}'.format(exporter.id)
                row = (old_url, exporter.build_url())

                writer.writerow(row)
