import operator
from functools import reduce

from django.utils.html import escape

from exporter.settings import BasketSettings, SearchSettings, \
    FilterSettings, GroupBySettings, FormatSettings, LinkSettings

def flatten_list(list_to_flatten):
    """ from list_to_flatten = [[1,2,3],[4,5,6], [7], [8,9]] to
       [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return reduce(operator.concat, list_to_flatten)

def _build_settings_from_POST(dict, limit=5000):
    """Build settings classes from the POST QuerySet"""
    options = {}
    search = {}
    formats = {}
    links = {}

    # We may used this some day
    # formats['language'] = dict.get('format_language')

    formats['bullets_type'] = dict.get('format_bullets_type')
    formats['bullets_text'] = escape(dict.get('format_bullet_text'))
    formats['bullets_order'] = dict.get('format_bullet_order')
    formats['format_name'] = dict.get('format_type')
    formats['has_clickable_authors'] = dict.get('link_has_clickable_authors')
    formats['has_clickable_titles'] = dict.get('link_has_clickable_titles')
    formats['language'] = dict.get('link_target_langage')

    links['has_readable_links'] = dict.get('link_has_readable_links')
    links['target_langage'] = dict.get('link_target_langage')
    if dict.get('link_has_fulltext'):
        links['fulltext'] = escape(dict.get('link_text_fulltext'))
    if dict.get('link_has_official'):
        links['official'] = escape(dict.get('link_text_official'))
    if dict.get('link_has_endnote'):
        links['endnote'] = escape(dict.get('link_text_endnote'))
    if dict.get('link_has_detailed_record'):
        links['detailed_record'] = escape(
            dict.get('link_text_detailed_record'))
    if dict.get('link_has_bibtex'):
        links['bibtex'] = escape(dict.get('link_text_bibtex'))

    options['format'] = FormatSettings(**formats)
    options['link'] = LinkSettings(**links)

    # Basket Mode
    if dict.get('search_basket_id'):
        search['basket_id'] = dict['search_basket_id']
        options['search'] = BasketSettings(**search)
    # Search Mode
    else:
        filters_settings = {}
        group_bys = {}

        if dict.get('search_pattern'):
            search['pattern'] = dict['search_pattern']
        if dict.get('search_field_restriction'):
            search['field_restriction'] = dict['search_field_restriction']
        if dict.get('search_collection'):
            search['collection'] = dict['search_collection']
        if dict.get('search_filter'):
            search_filter_list = []
            for string_filter in dict['search_filter'].split(","):
                search_filter_list.append(string_filter)
            search['filter'] = search_filter_list

        options['search'] = SearchSettings(**search)

        if dict.get('limit_first'):
            try:
                options['limit'] = int(dict['limit_number'])
            except ValueError:
                pass

        if options.get('limit') and limit:
            if options['limit'] > limit:
                options['limit'] = limit
        elif limit:
            options['limit'] = limit

        filters_settings['published'] = dict.get('filter_published')

        if filters_settings['published'] == 'range':
            filters_settings['published_from'] = dict.get(
                'filter_published_from')
            filters_settings['published_to'] = dict.get('filter_published_to')
        elif filters_settings['published'] == 'date':
            filters_settings['published_date'] = dict.get(
                'filter_published_date')

        if dict.get('group_by_first'):
            group_bys['first'] = dict['group_by_first']
        if dict.get('group_by_second'):
            group_bys['second'] = dict['group_by_second']
        if dict.get('group_by_doctype_display_headings'):
            group_bys['doctype_display_headings'] = True
        if dict.get('group_by_ordered_doctype_list'):
            group_bys['doctype_order'] = dict.get(
                'group_by_ordered_doctype_list').split(',')
        if dict.get('group_by_year_display_headings'):
            group_bys['year_display_headings'] = True
        group_bys['year_order'] = dict.get('group_by_year_order')
        if dict.get('group_by_year_seperate_pending'):
            group_bys['year_seperate_pending'] = False
        else:
            group_bys['year_seperate_pending'] = True

        options['filter'] = FilterSettings(**filters_settings)
        options['group_by'] = GroupBySettings(**group_bys)

    return options
