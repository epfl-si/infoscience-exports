import re
import csv
import json
import urllib.parse
import logging

from django.utils import timezone
from django.db import models
from django.db.models.manager import Manager

from django.contrib.postgres.fields import JSONField
from django.conf import settings

from exports.models import Export, LegacyExport, User


logger = logging.getLogger('migration')
search_logger = logging.getLogger('migration.search')
urls_logger = logging.getLogger('migration.urls')
skipped_logger = logging.getLogger('migration.skipped')
handling_logger = logging.getLogger('migration.handling')

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

    def load_exports_from_people(self, people_file_path, only_this_ids_from_legacy=[], subset=False):
        """
        Save as new exports from the people csv
        csv is sciper, username, src, email
        only_this_ids_from_legacy : if we want only a batch of migration
        subset : if you want to filter the od legacy exports that are too complex. See can_handle() for the complexity check
        """
        fallback_user = User.objects.get(username='delasoie')

        with open(people_file_path, 'r') as f:
            reader = csv.reader(f)
            people_full_list = list(reader)

        for row in people_full_list[1:]:
            username = row[0]
            email = row[1]
            sciper = row[2]
            box_id = row[3]
            language = row[4]
            legacy_export_url = row[5].strip()

            # we may need to ignore empty or no means
            if self.is_url_to_ignore(legacy_export_url) or \
               self.is_url_already_a_search(legacy_export_url) or \
               self.is_url_a_record(legacy_export_url):
                skipped_logger.debug(
                    "Ignoring an invalid legacy url : {}".format(legacy_export_url))
                continue

            legacy_export_id = self.get_legacy_export_id_from_url(legacy_export_url)

            if not legacy_export_id:
                skipped_logger.info(
                    "Skipping : invalid legacy export url for {}\n"
                    "Raw People data : {}".format(legacy_export_url, row))
                continue

            # if we are in selective mode, only do the one we want
            if only_this_ids_from_legacy:
                if not legacy_export_id in only_this_ids_from_legacy:
                    continue
                logger.info("----------------\n" \
                    "Doing the selective mode for People with legacy ID {}".format(legacy_export_id))

            try:
                exporter = SettingsModel.objects.get(id=legacy_export_id)
            except SettingsModel.DoesNotExist:
                skipped_logger.info(
                    "Skipping : no Settings model found for id {}\n"
                    "Raw People data : {}".format(legacy_export_id, row)
                )
                continue

            if subset:
                if not exporter.can_handle():
                    handling_logger.info(
                        "Skipping : This settings model is to tricky to be migrated"
                    )
                    continue

            # always create the export
            current_export = exporter.as_new_export()

            current_export.name = "People"

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

            current_export.user = export_user

            # now is it an update or a new ?
            existing_exports = Export.objects.filter(legacyexport__legacy_id=exporter.id).distinct()
            if existing_exports:
                existing_export = existing_exports[0]
                logger.debug("Updating Export id {} from the new build...".format(
                    existing_export.id))
                # it exists, so we will save to this id
                current_export.id = existing_export.id
                current_export.save()
            else:
                # it's new, a save will do it
                logger.debug("Creating a new Export ...")
                current_export.save()

            # now check for every refs, if this a new or an update
            current_legacy_export = LegacyExport(export=current_export,
                                                 legacy_id=legacy_export_id,
                                                 legacy_url=legacy_export_url,
                                                 language=language,
                                                 origin='PEOPLE',
                                                 origin_sciper=sciper,
                                                 origin_id=box_id,
                                                 raw_csv_entry=row,
                                                 )

            try:
                existing_legacy_export = current_export.legacyexport_set.get(legacy_id=legacy_export_id,
                                                                             language=language,
                                                                             origin='PEOPLE',
                                                                             origin_id=box_id,
                                                                             )
                # it's an update
                logger.debug("Updating a legacy export ref, id {} ...".format(existing_legacy_export.export_id))
                current_legacy_export.id = existing_legacy_export.id
                current_legacy_export.save()
                urls_logger.info("Resulting export url : {}".format(
                    settings.SITE_DOMAIN + existing_legacy_export.get_with_langage_absolute_url()))
            except LegacyExport.DoesNotExist:
                logger.debug("Creating new legacy export ref...")
                # it's new
                current_legacy_export.save()
                logger.debug("Created id {}".format(current_legacy_export.id))
                urls_logger.info("Resulting export url : {}".format(settings.SITE_DOMAIN + current_legacy_export.get_with_langage_absolute_url()))

    def load_exports_from_jahia(self, jahia_file_path, only_this_ids_from_legacy=[], subset=False):
        """
        Save as new exports from the jahia csv
        csv is id_jahia_ctn_entries,key_jahia_sites, site ,language_code,last_change_sciper,time_jahia_audit_log,last_changed_date,url_export,username,email
        only_this_url_from_legacy : if we want only a batch of migration
        subset : if you want to filter the od legacy exports that are too complex. See can_handle() for the complexity check
        """
        fallback_user = User.objects.get(username='delasoie')

        logger.debug("Doing selective {}".format(only_this_ids_from_legacy))

        with open(jahia_file_path, 'r') as f:
            reader = csv.reader(f)
            jahia_full_list = list(reader)

            logger.info("Raw jahia data : id_jahia_fields_data,id_jahia_ctn_entries,key_jahia_sites,site,language_code,username_jahia_audit_log,time_jahia_audit_log,FROM_UNIXTIME(log2.time_jahia_audit_log / 1000),value_jahia_fields_data,username,email")

        for row in jahia_full_list[1:]:
            jahia_id_fields_data = row[0]
            jahia_id = row[1]
            jahia_site_key = row[2]
            jahia_site_url = row[3]
            language = row[4]
            sciper = row[5]
            raw_audit_time = row[6]
            UNIXTIME_audit_time = row[7]  # FROM_UNIXTIME(log2.time_jahia_audit_log / 1000)
            legacy_export_url = row[8]
            username = row[9]
            email = row[10]

            # we may need to ignore empty or no means
            if self.is_url_to_ignore(legacy_export_url) or \
               self.is_url_already_a_search(legacy_export_url):
                skipped_logger.debug(
                    "Ignoring an invalid legacy url : {}".format(legacy_export_url))
                continue

            legacy_export_id = self.get_legacy_export_id_from_url(legacy_export_url)

            if not legacy_export_id and not only_this_ids_from_legacy:
                skipped_logger.debug(
                    "Skipping : invalid legacy export url for {}\n"
                    "Raw Jahia data : {}".format(legacy_export_url, row))
                continue

            # if we are in selective mode, only do the one we want
            if only_this_ids_from_legacy:
                if not legacy_export_id in only_this_ids_from_legacy:
                    skipped_logger.info(
                        "This jahia entry for Legacy id {} is not needed".format(
                            legacy_export_id))
                    continue
                logger.debug("----------------")
                logger.debug("Jahia entry {}".format(row))
                logger.info("Doing the selective mode for Jahia with legacy ID {}".format(legacy_export_id))

            try:
                exporter = SettingsModel.objects.get(id=legacy_export_id)
            except SettingsModel.DoesNotExist:
                skipped_logger.info(
                    "Skipping : no Settings model found for id {}\n"
                    "Raw Jahia data : {}".format(legacy_export_id, row)
                )
                continue

            if subset:
                if not exporter.can_handle():
                    handling_logger.info(
                        "Skipping : This settings model is to tricky to be migrated"
                    )
                    continue

            # always create the export
            current_export = exporter.as_new_export()

            current_export.name = "Jahia export ({})".format(jahia_site_key)

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

            current_export.user = export_user
            # now is it an update or a new ?
            existing_exports = Export.objects.filter(legacyexport__legacy_id=exporter.id).distinct()
            if existing_exports:
                existing_export = existing_exports[0]
                logger.debug("Updating Export id {} from the new build...".format(
                    existing_export.id))
                # it exists, so we will save to this id
                current_export.id = existing_export.id
                current_export.save()
            else:
                # it's new, a save will do it
                logger.debug("Creating a new Export ...")
                current_export.save()

            # now check for every refs, if this a new or an update
            current_legacy_export = LegacyExport(export=current_export,
                                         legacy_id=legacy_export_id,
                                         legacy_url=legacy_export_url,
                                         language=language,
                                         referenced_url=jahia_site_url,
                                         origin='JAHIA',
                                         origin_id=jahia_id_fields_data,
                                         origin_sciper=sciper,
                                         raw_csv_entry=row,
                                         # for regeneration purpose
                                         )

            try:
                existing_legacy_export = current_export.legacyexport_set.get(legacy_id=legacy_export_id,
                                                                             language=language,
                                                                             origin='JAHIA',
                                                                             origin_id=jahia_id_fields_data,
                                                                             )
                # it's an update
                logger.debug("Updating a legacy export ref, id {} ...".format(existing_legacy_export.export_id))
                current_legacy_export.id = existing_legacy_export.id
                current_legacy_export.save()
                urls_logger.info("Resulting export url : {}".format(
                    settings.SITE_DOMAIN + existing_legacy_export.get_with_langage_absolute_url()))
            except LegacyExport.DoesNotExist:
                logger.debug("Creating new legacy export ref...")
                # it's new
                current_legacy_export.save()
                logger.debug("Created id {}".format(current_legacy_export.id))
                urls_logger.info("Resulting export url : {}".format(settings.SITE_DOMAIN + current_legacy_export.get_with_langage_absolute_url()))


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

    def search_values(self):
        """ shortcut mainly for report on old key"""
        s = self.settings_as_dict
        search_key = {}

        if 'search_basket_id' in s and s['search_basket_id']:
            search_key['search_basket_id'] = s['search_basket_id']
        else:
            if 'search_pattern' in s and s['search_pattern']:
                search_key['search_pattern'] = s['search_pattern']
            if 'search_collection' in s and s['search_collection']:
                search_key['search_collection'] = s['search_collection']
            if 'search_field_restriction' in s and s['search_field_restriction']:
                search_key['search_field_restriction'] = s['search_field_restriction']
            if 'search_filter' in s and s['search_filter']:
                search_key['search_filter'] = s['search_filter']

        return search_key

    def can_handle(self):
        """ Some exports are too tricky to be valid
            This method is here to filter them
        """
        can_handle = False
        s = self.settings_as_dict
        # only do the one that have only a search_pattern
        if 'search_pattern' in s and s['search_pattern']:
            can_handle = True

            if 'search_collection' in s and s['search_collection']:
                can_handle = False
            if 'search_field_restriction' in s and s['search_field_restriction']:
                can_handle = False
            if 'search_filter' in s and s['search_filter']:
                can_handle = False

        if not can_handle:
            handling_logger.info(
                "Skipping : This settings model is "
                "to tricky to be migrated {}\nSearch values {}".format(self.id, self.search_values())
            )

        return can_handle

    def _get_search_pattern(self):
        search_logger.info("Doing search pattern conversion")
        search_logger.info("From {}".format(self.search_values()))

        s = self.settings_as_dict
        as_args = {}
        search_pattern = ''

        if 'search_pattern' in s and s['search_pattern']:
            search_pattern = s['search_pattern']
            search_logger.debug('pattern is : "{}"'.format(search_pattern))

            # look for minus symbol
            search_pattern_split = search_pattern.split(' ')
            if search_pattern_split:
                search_pattern_list = []
                for key in search_pattern_split:
                    # wrap in double-quotes when there is a minus and it is not already quoted
                    if key.find("-") != -1 and key[0] not in ["'", '"']:
                        search_pattern_list.append('"{}"'.format(key))
                    else:
                        search_pattern_list.append(key)
                search_pattern = " ".join(search_pattern_list)

            # uppercase AND and OR
            search_pattern = search_pattern.replace(' or ', ' OR ').replace(' and ', ' AND ')
            # replace YEAR=XXX by YEAR:XXX
            search_pattern = search_pattern.replace('YEAR=', 'YEAR:').replace('year=', 'year:')
            # doi:xxx -> doi:"xxxx"
            if search_pattern.find('doi:') != -1:
                new_search_pattern = []
                for one_split in search_pattern.split(' '):
                    try:
                        if one_split.find('doi:') != -1 and one_split[4] not in ['"', "'"] and \
                                        one_split[-1] not in ['"', "'"]:
                            doi_place = one_split.find('doi:')
                            new_search_pattern.append('doi:"' + one_split[doi_place+4:] + '"')
                        else:
                            new_search_pattern.append(one_split)
                    except ValueError:
                        new_search_pattern.append(one_split)

                search_pattern = " ".join(new_search_pattern)

            # add space when paranthesis search
            first_parenthesis = r'\(([^\s-])'
            second_parenthesis = r'([^\s-])\)'
            search_pattern = re.sub(first_parenthesis, r'( \1', search_pattern)
            search_pattern = re.sub(second_parenthesis, r'\1 )',search_pattern)
        else:
            search_logger.debug(
                "search_pattern is empty")

        # add date limit if needed
        # by default, all is need, so skip the date limit check
        if 'filter_published' in s and \
            s['filter_published'] == 'range' and \
            'filter_published_from' in s and \
            s['filter_published_from'] == 'all' and \
            'filter_published_to' in s and \
            s['filter_published_to'] == 'present':
            pass  # this is a convenient way to not do a negative if
        else:
          if 'filter_published' in s:
            if s['filter_published'] == 'range':
                from_year = None
                to_year = None
                if 'filter_published_from' in s and s['filter_published_from']:
                    from_year = s['filter_published_from']
                if 'filter_published_to' in s and s['filter_published_to']:
                    to_year = s['filter_published_to']
                if from_year:
                    if from_year == 'all':
                        search_pattern += ' year:'
                    else:
                        search_pattern += ' year:{}'.format(from_year)
                    if to_year:
                        if to_year == 'present':
                            search_pattern += '->now'
                        else:
                            search_pattern += '->{}'.format(to_year)
            elif s['filter_published'] == 'date':
                if 'filter_published_date' in s:
                    try:
                        last_x_years = int(s['filter_published_date'])
                        search_pattern += ' year:{}->now'.format(2018-last_x_years)
                    except ValueError:
                        if s['filter_published_date'] == 'current':
                            search_pattern += ' year:2018'

        # Do the exts
        exts = s.get('search_filter')

        if not exts:
            as_args['p'] = '{}'.format(search_pattern)
            search_logger.debug(
                "Filters are empty")
        else:
            """
           'collection:ARTICLE,review:REVIEWED,status:PUBLISHED,status:ACCEPTED,collection:PROC,review:ACCEPTED'
           => '( collection:ARTICLE AND collection:PROC ) OR ( review:REVIEWED ) OR ( status:PUBLISHED AND status:ACCEPTED )'
           """
            search_logger.debug(
                "exts found : {}".format(exts))

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
                ext_search_pattern += '( ' + ' OR '.join(values) + ' )'

            if search_pattern and search_pattern != '':
                search_pattern = '( ' + search_pattern + ' ) AND ' + ext_search_pattern
            else:
                search_pattern = ext_search_pattern

            as_args['p'] = search_pattern

        if search_pattern:
            search_logger.info('to New pattern : "{}"'.format(search_pattern))

        return as_args

    def _configuration_as_invenio_args(self):
        s = self.settings_as_dict
        invenio_vars = {}

        if 'search_basket_id' in s and s['search_basket_id']:
            logger.debug("Set has basket")
            invenio_vars['bskid'] = s['search_basket_id']
            invenio_vars['of'] = 'xm'
            return invenio_vars

        invenio_vars.update(self._get_search_pattern())

        if 'search_field_restriction' in s and s['search_field_restriction']:
            search_logger.debug("field_restriction is {}".format(s['search_field_restriction']))
            invenio_vars['f1'] = s['search_field_restriction']

        if 'search_collection' in s and s['search_collection']:
            search_logger.debug("collection is {}".format(
                s['search_collection']))
            if not invenio_vars.get('c'):
                invenio_vars['c'] = []
            invenio_vars['c'].append(s['search_collection'])

        if 'group_by_year_order' in s and s['group_by_year_order']:
            if s['group_by_year_order'] == 'asc':
                invenio_vars['so'] = 'a'
            else:
                invenio_vars['so'] = 'd'

        if 'limit_first' in s and s['limit_first']:
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
            raise ValueError("No basket at the moment for advanced search url")

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

        search_url = 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(
            invenio_args, doseq=True)

        urls_logger.debug("Advanced search url built : {}".format(search_url))

        return search_url

    def build_search_url(self, invenio_vars={}, limit=None):
        """ build the infoscience url where it probably come from"""
        invenio_args = self._configuration_as_invenio_args()

        invenio_args.update(invenio_vars)

        if limit:
            invenio_vars['rg'] = limit

        if invenio_vars.get('bskid'):
            search_url = 'https://infoscience.epfl.ch/yourbaskets/display_public?' + urllib.parse.urlencode(invenio_args, doseq=True)

        else:
            search_url = 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(invenio_args, doseq=True)

        urls_logger.debug("New search url built : {}".format(search_url))
        return search_url

    def as_new_export(self):
        logger.debug("Building a new export from Legacy ID {}...".format(self.id))
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

        if 'link_has_clickable_authors' in s and s[
            'link_has_clickable_authors']:
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
                if 'group_by_year_display_headings' in s and s['group_by_year_display_headings']:
                    new_export.groupsby_type = 'YEAR_TITLE'
                if 'group_by_second' in s and s['group_by_second']:
                    if 'group_by_doctype_display_headings' in s and s[
                        'group_by_doctype_display_headings']:
                        new_export.groupsby_doc = 'DOC_TITLE'
            elif s['group_by_first'] == 'doctype':
                new_export.groupsby_type = 'DOC_TITLE'
                if 'group_by_second' in s and s['group_by_second']:
                    if 'group_by_year_display_headings' in s and s[
                        'group_by_year_display_headings']:
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
