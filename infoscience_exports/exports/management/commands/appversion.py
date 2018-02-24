from django.core.management.base import BaseCommand

from exports import format_version


class Command(BaseCommand):

    help = "Display version, release or build number (or all)"

    def add_arguments(self, parser):
        parser.add_argument('label', nargs='*', type=str)

    # A command must define handle()
    def handle(self, label, *args, **options):
        self.stdout.write(format_version(label=label))
