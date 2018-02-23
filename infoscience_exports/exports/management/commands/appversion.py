from django.core.management.base import LabelCommand, CommandError

from exports import __version__, __build__, __release__


class Command(LabelCommand):

    help = "Display version or build number"
    label = "version, release, build, all"

    # A command must define handle()
    def handle_label(self, label, **options):
        if label == 'version':
            self.stdout.write(__version__)
        elif label == 'build':
            self.stdout.write(__build__)
        elif label == 'release':
            self.stdout.write(__release__)
        elif label == 'all':
            self.stdout.write("release {}, build {}, version {}".format(
                __release__, __build__, __version__
            ))
        else:
            raise CommandError('label unsupported, should be in [{}]'.format(self.label))
