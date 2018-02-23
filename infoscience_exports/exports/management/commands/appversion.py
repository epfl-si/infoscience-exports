from django.core.management.base import LabelCommand

from exports import format_version


class Command(LabelCommand):

    help = "Display version or build number"
    label = "version, release, build, all"

    # A command must define handle()
    def handle_label(self, label, **options):
        return format_version(label)
