import json
import urllib.parse

from django.db import models
from django.db.models.manager import Manager

from django.contrib.postgres.fields import JSONField


class SettingsManager(Manager):
    def get_settings_ids_for_lab(self, lab):
        full_path = lab.get_coll_name() if not lab.archived else None
        query = r'unit:%s|%s' % (lab.acronym, full_path)
        
        return self.filter(settings__iregex=query)


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
        search_pattern = ''

        if 'search_pattern' in s and s['search_pattern']:
            search_pattern = s['search_pattern']

        return search_pattern

    def _configuration_as_invenio_args(self):
        s = self.settings_as_dict
        invenio_vars = {}

        if 'search_basket_id' in s and s['search_basket_id']:
            invenio_vars['bskid'] = s['search_basket_id']
            invenio_vars['of'] = 'xm'
            return invenio_vars

        invenio_vars['p'] = self._get_search_pattern()

        if 'search_field_restriction' in s and s['search_field_restriction']:
            invenio_vars['f'] = s['search_field_restriction']

        if 'search_collection' in s and s['search_collection']:
            invenio_vars['cc'] = s['search_collection']

        if 'group_by_year_order' in s and s['group_by_year_order']:
            if s['group_by_year_order'] == 'asc':
                invenio_vars['so'] = 'a'
            else:
                invenio_vars['so'] = 'd'

        if 'limit_number' in s and s['limit_number']:
            invenio_vars['rg'] = s['limit_number']

        if 'search_filter' in s:
            pass
            # logger.warning(("Warning, in the new export system, search filter is no more :\n{}"
            #                  .format(s['search_filter']))

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
            'd1d': '29',
            'd1m': '01',
            'd1y': '2018',
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
            invenio_args)

    def build_search_url(self, invenio_vars={}, limit=None):
        """ build the infoscience url where it probably come from"""
        invenio_args = self._configuration_as_invenio_args()

        invenio_args.update(invenio_vars)

        if limit:
            invenio_vars['rg'] = limit

        if invenio_vars.get('bskid'):
            return 'https://infoscience.epfl.ch/yourbaskets/display_public?' + urllib.parse.urlencode(invenio_args)
        else:
            return 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(invenio_args)
