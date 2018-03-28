from django.core.management.base import BaseCommand

from exporter.models import SettingsModel
from exports.models import Export, User

"""
dump with 
manage.py dumpdata -o ./exports_from_32.json exporter

load with
make load-dump
"""


class Command(BaseCommand):

    help = "Migrate exports from infoscience-legacy base to the new format"

    # A command must define handle()
    def handle(self, *args, **options):
        import pdb

        exporter = SettingsModel.objects.latest('id')
        s = exporter.settings_as_dict()

        self.stdout.write("doing {}...".format(exporter.id))
        new_export = Export()

        new_export.name = "from old export {}".format(exporter.id)

        # TODO created_at, updated_at
        new_export.created_at = exporter.created_at
        new_export.updated_at = exporter.updated_at

        # url
        new_export.url = exporter.build_url()

        # format type
        if 'format_type' in s and s['format_type']:
            if 'short' in s['format_type']:
                new_export.formats_type = 'SHORT'
            elif 'detailed' in s['format_type']:
                new_export.formats_type = 'DETAILED'
            elif 'full' in s['format_type']:
                new_export.formats_type = 'DETAILED'
                new_export.show_summary = True
            if '_authors' in s['format_type']:
                new_export.show_linkable_authors = True

        # group by
        # TODO:
        # if 'group_by_year_seperate_pending' in s and s['group_by_year_seperate_pending']:
        #     new_export.show_pending_publications = True
        #
        # if 'group_by_first' in s and s['group_by_first'] == 'year':
        #     new_export.groupsby_year = 'YEAR_TITLE'
        #
        #     if 'group_by_second' in s and s['group_by_first'] == 'year':
        #
        #     # old default groupby, if not "years as title" and not second lvl
        #     # this is the default listing
        #     if 'group_by_year_display_headings' in s and s['group_by_year_display_headings']:
        #         new_export.groupsby_year = 'YEAR_TITLE'

        # bullets
        if 'format_bullet_order' in s and s['format_bullet_order']:
            new_export.show_detailed = True

        if 'format_bullet_text' in s and s['format_bullet_text']:
            if s['format_bullet_text'] == '*':
                new_export.bullets_type = 'CHARACTER_STAR'
            elif s['format_bullet_text'] == '-':
                new_export.bullets_type = 'CHARACTER_MINUS'
            else:  # default
                new_export.bullets_type = 'CHARACTER_STAR'

        # links
        if 'link_has_detailed_record' in s and s['link_has_detailed_record']:
            new_export.show_detailed = True
        if 'link_has_fulltext' in s and s['link_has_fulltext']:
            new_export.show_fulltext = True
        if 'link_has_official' in s and s['link_has_official']:
            new_export.show_viewpublisher = True


        # divers
        if 'link_has_readable_links' in s and s['link_has_readable_links']:
            new_export.show_links_for_printing= True


        #TODO set the right user
        new_export.user = User.objects.all()[0]
        new_export.save()
        self.stdout.write("...saving {}".format(new_export.id))
        pdb.set_trace()
