import re

from urllib.request import urlopen
from urllib.error import HTTPError

from django.test import RequestFactory
from django.core.management.base import BaseCommand
from django.conf import settings

from exports.models import LegacyExport
from exports import views

class Command(BaseCommand):

    help = "Add to legacy export a quality check on number of content trough the two systems"

    def handle(self, *args, **options):

        for legacy_export in LegacyExport.objects.all():
            old_url_content = legacy_export.legacy_url.replace(
                'infoscience.epfl.ch', 'test-infoscience.epfl.ch')
            self.stdout.write("Doing legacy {}".format(old_url_content))

            # TODO: add filter before 29.01.2018
            new_export_url = legacy_export.export.url
            old_infoscience_to_read = ''
            new_export_to_read = ''
            try:
                old_infoscience_to_read = urlopen(old_url_content).read().decode('utf-8')
                new_export_to_read = urlopen(new_export_url+'&of=xm').read().decode('utf-8')
            except HTTPError:
                self.stdout.write(
                    "unknown address, leaving")
                continue

            # cache_key = legacy_export.export.get_cache_key_for_view('en')
            # request = RequestFactory().get(legacy_export.export.get_absolute_url())
            # new_export_to_read = str(views.ExportView.as_view()(request, pk=legacy_export.export.id).content)

            old_count = old_infoscience_to_read.count("infoscience_record")
            new_count = 0

            text_to_find = r"<!-- Search-Engine-Total-Number-Of-Results: (\d+)"
            m = re.search(text_to_find, new_export_to_read)
            if not m:
                # we found nothing, skip this
                self.stdout.write("Look like there is no new record, end here")
                continue

            if m.group(1):
                new_count = int(m.group(1))

            if old_count and new_count:
                legacy_export.content_delta = abs(old_count - new_count)
                self.stdout.write("delta found %s" % abs(old_count - new_count))
                legacy_export.save()
            else:
                self.stdout.write("Can't do delta with "
                                  "no old {} or new count {}".format(old_count, new_count))
