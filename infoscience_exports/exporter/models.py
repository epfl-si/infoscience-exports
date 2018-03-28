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
    
    def __unicode__(self):
        return str(self.get_settings_as_classes())

    def settings_as_dict(self):
        return json.loads(self.settings)

    def build_url(self):
        """ build the infoscience url where it probably come from"""
        s = self.settings_as_dict()

        invenio_vars = {}

        if 'search_basket_id' in s and s['search_basket_id']:
            invenio_vars['bskid'] = s['search_basket_id']
            invenio_vars['category'] = 'P'
            invenio_vars['topic'] = 'default'
            invenio_vars['of'] = 'xm'
            return 'https://infoscience.epfl.ch/yourbaskets/display?' + urllib.parse.urlencode(invenio_vars)
        else:
            if 'search_pattern' in s and s['search_pattern']:
                invenio_vars['p'] = s['search_pattern']

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
                # TODO
                # logger.warning(("Warning, in the new export system, search filter is no more :\n{}"
                #                  .format(s['search_filter']))

            return 'https://infoscience.epfl.ch/search?' + urllib.parse.urlencode(invenio_vars)
