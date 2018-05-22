import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from exporter.models import Export


class Command(BaseCommand):

    help = "Generate a csv file, where all the useful information are set"

    def add_arguments(self, parser):
        parser.add_argument('--output', nargs='*', type=str)

    def handle(self, output, *args, **options):
        if not output:
            raise CommandError("Missing the 'output' argument")

        with open(output[0], 'w') as f:
            header = ['id', 'name', 'created_at', 'updated_at', 'absolute_url', 'url', 'legacy_url', 'user']

            for field in Export._meta.fields:
                if field.name not in header:
                    header.append(field.name)

            writer = csv.writer(f)

            writer.writerow(header)

            for export in Export.objects.all().select_related('user'):
                try:
                    export.legacy_url = 'https://test-infoscience.epfl.ch/curator/export/{}/'.format(export.legacyexport_set.all()[0].legacy_id)
                except IndexError:  # not legacy linked
                    export.legacy_url = ''

                export.absolute_url = settings.SITE_DOMAIN + export.get_absolute_url()
                row = []

                for field_name in header:
                    row.append(getattr(export, field_name))

                writer.writerow(row)
