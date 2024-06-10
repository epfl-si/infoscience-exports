import os
import time

from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse

from exports.models.export import Export


# Run example:
# DJANGO_COLORS="warning=red;error=red;notice=yellow;success=green" python infoscience_exports/manage.py --delay 1 forcerenderall
class Command(BaseCommand):
    help = 'Force rendering all exports. Mainly used before the migration to dspace. It fills the permanent db cache.'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--delay',
            help='Choose the time between each call, in seconds. It is a string representing a float value.',
            default='0.5',
        )
        parser.add_argument(
            '--skipdone',
            help="Don't redo the one already db cached",
            action='store_true'
        )

    def handle(self, *args, **options):
        client = Client(SERVER_NAME='localhost')

        count_export_processed = 0

        export_to_process = Export.objects.filter(server_engine='invenio').order_by('id')

        if options['skipdone']:
            self.style.SUCCESS(f'Skipping the one already db cached')
            export_to_process = export_to_process.filter(last_rendered_page__isnull=True)

        total_export = export_to_process.count()

        self.stdout.write(
            self.style.SUCCESS(f'Starting the call and render of all exports in db. Expect {total_export} calls.'))

        for export in export_to_process:
            self.stdout.write(self.style.NOTICE(
                '-----')
            )
            self.stdout.write(self.style.NOTICE(
                f'export.id: {export.id}')
            )
            self.stdout.write(self.style.NOTICE(
                f'Progress: {count_export_processed + 1}/{total_export}')
            )

            request_url = f'{os.getenv("SITE_URL")}/{str(export.id)}/'

            self.stdout.write(self.style.NOTICE(
                f'Calling: {request_url} to cache result of {export.url}')
            )

            # call the view to do the render
            response = client.get(request_url)
            count_export_processed += 1

            # check for http response
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(
                    '200 ok returned')
                )
            else:
                self.stdout.write(self.style.WARNING(
                    f'Not a 200 returned. Error was : {response.status_code}'
                ))

            # refresh the object and check for his data
            export = Export.objects.get(id=export.id)

            # check for render
            if export.last_rendered_page is not None:
                self.stdout.write(self.style.SUCCESS(
                    'Successfully saved render into db')
                )
            else:
                self.stdout.write(self.style.WARNING(
                    'db field is still empty after the call :(')
                )

            time.sleep(float(options.get('delay', '0.5')))
