import re
import csv
import json
import urllib.parse
import logging

from django.db import models
from django.db.models.manager import Manager

from django.contrib.postgres.fields import JSONField

from exports.models import Export, LegacyExport, User


logger = logging.getLogger('migration')

export_id_extractors = [
    r'^(?:https|http)://infoscience.epfl.ch/curator/export/(\d+)/?.*',
    r'^(?:https|http)://infoscience.epfl.ch/curator/publications/exporter/(\d+)/?.*',
]

export_ignores = [r'^https://infoscience.epfl.ch/publication-exports/(\d+)/?.*',
                  r'^http://$',
                  r'^https://$'
                  ]

export_search_identifier = r'^(?:https|http)://infoscience.epfl.ch/search\?.*'
export_record_identifier = r'^(?:https|http)://infoscience.epfl.ch/record/.*'


class SettingsManager(Manager):
    def get_settings_ids_for_lab(self, lab):
        full_path = lab.get_coll_name() if not lab.archived else None
        query = r'unit:%s|%s' % (lab.acronym, full_path)
        
        return self.filter(settings__iregex=query)

    @staticmethod
    def get_legacy_export_id_from_url(url):
        for extractor in export_id_extractors:
            matched = re.search(extractor, url)
            if matched:
                return matched.group(1)

    @staticmethod
    def is_url_to_ignore(url):
        should_ignore = False
        for ignore in export_ignores:
            matched = re.search(ignore, url)
            if matched:
                should_ignore = True
                break

        return should_ignore

    @staticmethod
    def is_url_already_a_search(url):
        matched = re.search(export_search_identifier, url)
        if matched:
            return True

    @staticmethod
    def is_url_a_record(url):
        matched = re.search(export_record_identifier, url)
        if matched:
            return True

    def load_exports_from_people(self, people_file_path):
        """
        Save as new exports from the people csv
        csv is sciper, username, src, email
        """
        fallback_user = User.objects.get(username='delasoie')

        with open(people_file_path, 'r') as f:
            reader = csv.reader(f)
            people_full_list = list(reader)

        for row in people_full_list[1:]:
            sciper = row[0]
            username = row[1]
            legacy_export_url = row[2].strip()
            email = row[3]

            # we may need to ignore empty or no means
            if self.is_url_to_ignore(legacy_export_url):
                continue

            # it may be a search directly, so we don't have the legacy export
            if self.is_url_already_a_search(legacy_export_url):
                new_export = Export(url=legacy_export_url)
            elif self.is_url_a_record(legacy_export_url):
                new_export = Export(url=legacy_export_url, formats_type='DETAILED')
            else:
                legacy_export_id = self.get_legacy_export_id_from_url(legacy_export_url)

                if not legacy_export_id:
                    logger.info(
                        "Skipping : invalid legacy export url for {}\n"
                        "Raw People data : {}".format(legacy_export_url, row))
                    continue
                try:
                    exporter = SettingsModel.objects.get(id=legacy_export_id)
                except SettingsModel.DoesNotExist:
                    logger.info(
                        "Skipping : no Settings model found for id {}\n"
                        "Raw People data : {}".format(legacy_export_id, row)
                    )
                    continue

                new_export = exporter.as_new_export()

            new_export.name = "People".format(sciper)

            if not username:
                export_user = fallback_user
            else:
                export_user = User.objects.get_or_create(username=username)[0]
                if email:
                    export_user.email = email
                if sciper:
                    export_user.sciper = sciper
                if email or sciper:
                    export_user.save()

            new_export.user = export_user
            new_export.save()

            # add info that created this export
            legacy_export = LegacyExport(export=new_export,
                                         legacy_url=legacy_export_url,
                                         origin='PEOPLE',
                                         origin_sciper=sciper,
                                         raw_csv_entry=row,  # for regeneration purpose
                                         )

            legacy_export.save()

    def load_exports_from_jahia(self, jahia_file_path):
        """
        Save as new exports from the jahia csv
        csv is id_jahia_ctn_entries,key_jahia_sites, site ,language_code,last_change_sciper,time_jahia_audit_log,last_changed_date,url_export,username,email
        """
        fallback_user = User.objects.get(username='delasoie')

        with open(jahia_file_path, 'r') as f:
            reader = csv.reader(f)
            jahia_full_list = list(reader)

            logger.info("Raw jahia data : id_jahia_ctn_entries,key_jahia_sites, site ,language_code,last_change_sciper,time_jahia_audit_log,last_changed_date,url_export,username,email")

        for row in jahia_full_list[1:]:
            jahia_id = row[0]
            jahia_site_key = row[1]
            jahia_site_url = row[2]
            language = row[3]
            sciper = row[4]
            raw_audit_time = row[5]
            UNIXTIME_audit_time = row[6]  # FROM_UNIXTIME(log2.time_jahia_audit_log / 1000)
            legacy_export_url = row[7]
            username = row[8]
            email = row[9]

            # we may need to ignore empty or no means
            if self.is_url_to_ignore(legacy_export_url):
                continue

            # it may be a search directly, so we don't have the legacy export
            if self.is_url_already_a_search(legacy_export_url):
                new_export = Export(url=legacy_export_url)
            else:
                legacy_export_id = self.get_legacy_export_id_from_url(legacy_export_url)

                if not legacy_export_id:
                    logger.info(
                        "Skipping : invalid legacy export url for {}\n"
                        "Raw Jahia data : {}".format(legacy_export_url, row))
                    continue
                try:
                    exporter = SettingsModel.objects.get(id=legacy_export_id)
                except SettingsModel.DoesNotExist:
                    logger.info(
                        "Skipping : no Settings model found for id {}\n"
                        "Raw Jahia data : {}".format(legacy_export_id, row)
                    )
                    continue

                new_export = exporter.as_new_export()

            new_export.name = "Jahia export ({})".format(jahia_site_key)

            if not username:
                export_user = fallback_user
            else:
                export_user = User.objects.get_or_create(username=username)[0]
                if email:
                    export_user.email = email
                if sciper:
                    export_user.sciper = sciper
                if email or sciper:
                    export_user.save()

            new_export.user = export_user
            new_export.save()


            # add info that created this export
            legacy_export = LegacyExport(export=new_export,
                                         legacy_url=legacy_export_url,
                                         language=language,
                                         referenced_url=jahia_site_url,
                                         origin='JAHIA',
                                         origin_sciper=sciper,
                                         raw_csv_entry=row,  # for regeneration purpose
                                         )

            legacy_export.save()


class SettingsModel(models.Model):
    objects = SettingsManager()
    
    settings = JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    _settings_as_dict = {}
    
    def __unicode__(self):
        return str(self.get_settings_as_classes())

    @property
    def settings_as_dict(self):
        if not self._settings_as_dict:
            self._settings_as_dict = json.loads(self.settings)
        return self._settings_as_dict

    def _get_search_pattern(self):
        s = self.settings_as_dict
        as_args = {}
        search_pattern = ''

        if 'search_pattern' in s and s['search_pattern']:
            search_pattern = s['search_pattern']

        exts = s.get('search_filter')

        if not exts:
            as_args['p'] = '{}'.format(search_pattern)
        else:
            """
           'collection:ARTICLE,review:REVIEWED,status:PUBLISHED,status:ACCEPTED,collection:PROC,review:ACCEPTED'
           => '(collection:ARTICLE AND collection:PROC) OR (review:REVIEWED) OR (status:PUBLISHED AND status:ACCEPTED)'
           """
            ext_search_pattern = ""
            # regroup first
            regrouped_index = {}
            for ext in exts.split(','):
                if not regrouped_index.get(ext[:ext.find(':')]):
                    regrouped_index[ext[:ext.find(':')]] = []
                regrouped_index[ext[:ext.find(':')]].append(ext)

            for key, values in regrouped_index.items():
                if key == 'fulltext':
                    """ fulltext search is no more a feature """
                    continue
                if ext_search_pattern:
                    ext_search_pattern += ' AND '
                ext_search_pattern += '(' + ' OR '.join(values) + ')'

            if search_pattern and search_pattern != '':
                search_pattern = '(' + search_pattern + ') AND ' + ext_search_pattern
            else:
                search_pattern = ext_search_pattern

            as_args['p'] = search_pattern

        return as_args

    def _configuration_as_invenio_args(self):
        s = self.settings_as_dict
        invenio_vars = {}

        if 'search_basket_id' in s and s['search_basket_id']:
            invenio_vars['bskid'] = s['search_basket_id']
            invenio_vars['of'] = 'xm'
            return invenio_vars

        invenio_vars.update(self._get_search_pattern())

        if 'search_field_restriction' in s and s['search_field_restriction']:
            invenio_vars['f1'] = s['search_field_restriction']

        if 'search_collection' in s and s['search_collection']:
            if not invenio_vars.get('c'):
                invenio_vars['c'] = []
            invenio_vars['c'].append(s['search_collection'])

        if 'group_by_year_order' in s and s['group_by_year_order']:
            if s['group_by_year_order'] == 'asc':
                invenio_vars['so'] = 'a'
            else:
                invenio_vars['so'] = 'd'

        if 'limit_number' in s and s['limit_number']:
            invenio_vars['rg'] = s['limit_number']

        return invenio_vars

    def build_advanced_search_url(self, invenio_vars={}, limit=None):
        """ build the infoscience url where it probably come from, but
        in an advanced search fashion
        """
        invenio_args = self._configuration_as_invenio_args()

        if limit:
            invenio_vars['rg'] = limit

        invenio_args.update(invenio_vars)

        # dont do basket at the moment
        if invenio_args.get('bskid'):
            raise ValueError("No basket at the moment")

        search_pattern = invenio_args.get('p')

        # add the advanced search options
        # see https://github.com/inveniosoftware/invenio/blob/5df3f3ae79a26724a28e9e77f576a5d021d1f4f9/modules/websearch/lib/search_engine.py#L5454
        advanced_search_vars = {
            # uncomment for modified instead of added
            # 'dt': 'm',
            'as': '1',
            'm1': 'a',
            'action_search': 'Search',
            'p1': search_pattern,
        }

        # this as been moved to p1
        if invenio_args.get('p'):
            del invenio_args['p']

        invenio_args.update(advanced_search_vars)

        return 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(
            invenio_args, doseq=True)

    def build_search_url(self, invenio_vars={}, limit=None):
        """ build the infoscience url where it probably come from"""
        invenio_args = self._configuration_as_invenio_args()

        invenio_args.update(invenio_vars)

        if limit:
            invenio_vars['rg'] = limit

        if invenio_vars.get('bskid'):
            return 'https://infoscience.epfl.ch/yourbaskets/display_public?' + urllib.parse.urlencode(invenio_args, doseq=True)
        else:
            return 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(invenio_args, doseq=True)

    def as_new_export(self):
        new_export = Export()

        new_export.name = "Imported export {}".format(self.id)

        s = self.settings_as_dict
        new_export.created_at = self.created_at
        new_export.updated_at = self.updated_at

        new_export.url = self.build_search_url()


        # format type
        if 'format_type' in s and s['format_type']:
            if 'ENACFULL' in s['format_type']:
                new_export.show_thumbnail = True
                new_export.formats_type = 'DETAILED'
                new_export.show_summary = True
                new_export.show_article_volume = True
                new_export.show_article_volume_number = True
                new_export.show_article_volume_pages = True
                new_export.show_thesis_directors = True
                new_export.show_thesis_pages = True
                new_export.show_report_working_papers_pages = True
                new_export.show_conf_proceed_place = True
                new_export.show_conf_proceed_date = True
                new_export.show_conf_paper_journal_name = True
                new_export.show_book_isbn = True
                new_export.show_book_doi = True
                new_export.show_book_chapter_isbn = True
                new_export.show_book_chapter_doi = True
                new_export.show_patent_status = True
            else:
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
        if 'group_by_year_seperate_pending' in s and s[
            'group_by_year_seperate_pending']:
            new_export.show_pending_publications = True

        new_export.groupsby_type = 'NONE'
        new_export.groupsby_doc = 'NONE'
        new_export.groupsby_year = 'NONE'

        if 'group_by_first' in s:
            if s['group_by_first'] == 'year':
                if 'group_by_year_display_headings' in s and s[
                    'group_by_year_display_headings']:
                    new_export.groupsby_type = 'YEAR_TITLE'
                if 'group_by_second' in s and s['group_by_second'] == 'doctype':
                    new_export.groupsby_doc = 'DOC_TITLE'
            elif s['group_by_first'] == 'doctype':
                new_export.groupsby_type = 'DOC_TITLE'
                if 'group_by_second' in s and s['group_by_second'] == 'year':
                    new_export.groupsby_year = 'YEAR_TITLE'

        # bullets
        if 'format_bullet_order' in s and s['format_bullet_order']:
            new_export.show_detailed = True

        if 'format_bullets' in s and s['format_bullets']:
            if 'format_bullets_type' in s:
                if s['format_bullets_type'] == 'text':
                    if 'format_bullet_text' in s and s['format_bullet_text']:
                        if s['format_bullet_text'] == '*':
                            new_export.bullets_type = 'CHARACTER_STAR'
                        elif s['format_bullet_text'] == '-':
                            new_export.bullets_type = 'CHARACTER_MINUS'
                        else:  # default
                            new_export.bullets_type = 'CHARACTER_STAR'
                elif s['format_bullets_type'] == 'number':
                    if 'format_bullet_order' in s:
                        if s['format_bullet_order'] == 'desc':
                            new_export.bullets_type = 'NUMBER_DESC'
                        elif s['format_bullet_order'] == 'asc':
                            new_export.bullets_type = 'NUMBER_ASC'

        # links
        if 'link_has_detailed_record' in s and s['link_has_detailed_record']:
            new_export.show_detailed = True
        if 'link_has_fulltext' in s and s['link_has_fulltext']:
            new_export.show_fulltext = True
        if 'link_has_official' in s and s['link_has_official']:
            new_export.show_viewpublisher = True

        # divers
        if 'link_has_readable_links' in s and s['link_has_readable_links']:
            new_export.show_links_for_printing = True

        return new_export
