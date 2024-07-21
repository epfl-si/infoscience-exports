import os
from logging import getLogger

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from urllib.parse import parse_qs, urlsplit
from itertools import groupby
from operator import itemgetter
from furl import furl

from .marc21xml import import_marc21xml
from .messages import get_message

logger = getLogger(__name__)


DOC_TYPE_ORDERED = {
    'Journal Articles': _("Journal Articles"),
    'Conference Papers': _("Conference Papers"),
    'Reviews': _("Reviews"),
    'Books': _("Books"),
    'Theses': _("Theses"),
    'Book Chapters': _("Book Chapters"),
    'Conference Proceedings': _("Conference Proceedings"),
    'Working Papers': _("Working Papers"),
    'Reports': _("Reports"),
    'Posters': _("Posters"),
    'Talks': _("Talks"),
    'Standards': _("Standards"),
    'Patents': _("Patents"),
    'Student Projects': _("Student Projects"),
    'Teaching Resources': _("Teaching Resources"),
    'Media': _("Media"),
    'Datasets': _("Datasets"),
}


def get_groups(options, notices, attr, subattr):
    groups_list = []
    for key, items in groupby(notices, itemgetter(attr)):
        subgroups_list = []
        for subkey, subitems in groupby(items, itemgetter(subattr)):
            if subattr == 'Doc_Type' and subkey not in DOC_TYPE_ORDERED:
                logger.error('Doc Type not recognized: ' + subkey)
            list2 = [{'title': DOC_TYPE_ORDERED.get(subkey, subkey)}]  # for year and doc_type
            list2.extend(list(subitems))
            subgroups_list.append(list2)
        if attr == 'Doc_Type' and key not in DOC_TYPE_ORDERED:
            logger.error('Doc Type not recognized: ' + key)
        list1 = [{'title': DOC_TYPE_ORDERED.get(key, key)}]  # for year and doc_type
        list1.extend(list(subgroups_list))
        groups_list.append(list1)
    return groups_list


def get_sorted_by_doc_types(notices):
    notices = sorted(notices, key=lambda k: (k['Doc_Type']))
    groups_list = []
    groups_head = []
    for key, items in groupby(notices, itemgetter('Doc_Type')):
        groups_list.append(list(items))
        groups_head.append(key)
    groups_list_ordered = []
    doc_type_keys = DOC_TYPE_ORDERED.keys()
    for key in doc_type_keys:
        for index, head in enumerate(groups_head):
            if head == key:
                groups_list_ordered.extend(groups_list[index])
    # add doc_types not listed in DOC_TYPE_ORDERED
    for index, head in enumerate(groups_head):
        if head not in doc_type_keys:
            groups_list_ordered.extend(groups_list[index])
    return groups_list_ordered


def get_sorted_by_year(notices, url):
    queries = parse_qs(urlsplit(url).query)
    is_ascending = queries.get('so', ['d'])[0] == "a"
    if is_ascending:
        notices = sorted(notices, key=lambda k: k['Publication_Year'])
    else:
        notices = sorted(notices, key=lambda k: k['Publication_Year'], reverse=True)
    return notices


def setbullets(notices, bullet_choice, notices_length):
    index = 1
    for groups in notices:
        for notices in groups:
            is_first = True
            if len(notices) == 1:
                continue
            for notice in notices:
                if is_first:
                    is_first = False
                elif bullet_choice == 'CHARACTER_STAR':
                    notice['bulleting'] = '*'
                elif bullet_choice == 'CHARACTER_MINUS':
                    notice['bulleting'] = '-'
                elif bullet_choice == 'NUMBER_ASC':
                    notice['bulleting'] = '[' + str(index) + ']'
                    index += 1
                elif bullet_choice == 'NUMBER_DESC':
                    notice['bulleting'] = '[' + str(notices_length - index + 1) + ']'
                    index += 1


def modify_url(url, queries, option, default, force_default):
    result = url
    if option in queries:
        if force_default:
            value = option + "=" + queries[option][0]
            result = url.replace(value, option + "=" + default)
    else:
        # empty option
        value = "?" + option + "=&"
        if value in url:
            result = url.replace(value, "?" + option + "=" + default + "&")
        else:
            value = "&" + option + "="
            if value in url:
                result = url.replace(value, "&" + option + "=" + default)
            else:
                result = url + "&" + option + "=" + default
    return result


def convert_url_for_dspace(url):
    # as we are on dspace, some parameters convert parameters for dspace, with python-requests
    # get the latest built URL and reparse it
    f = furl(url)

    # by default add this index
    if 'configuration' not in f.args:
        f.args['configuration'] = 'researchoutputs'

    if 'p' in f.args:
        f.args['query'] = f.args['p']
        del f.args['p']

    if 'query' in f.args:
        if 'recid:' in f.args['query']:
            # direct search with p=recid:'51128';
            # becomes query=cris.legacyId:51128
            f.args['query'] = f.args['query'].replace('recid:', 'cris.legacyId:')
        if 'unit:' in f.args['query']:
            f.args['query'] = f.args['query'].replace('unit:', 'dc.description.sponsorship:')

    if 'rg' in f.args and 'spc.rpp' not in f.args:
        f.args['spc.rpp'] = f.args['rg']
        del f.args['rg']

    if 'sf' in f.args and f.args['sf'] == 'year' and 'dc.date.issued' not in f.args:
        f.args['spc.sf'] = 'dc.date.issued'
        del f.args['sf']

    if 'so' in f.args and 'spc.sd' not in f.args:
        if f.args['so'] == 'd':
            f.args['spc.sd'] = 'DESC'
        elif f.args['so'] == 'a':
            f.args['spc.sd'] = 'ASC'
        del f.args['so']

    if 'c' in f.args:
        del f.args['c']

    return f.url


def validate_url(url):
    queries = parse_qs(urlsplit(url).query)

    if '?' not in url:
        # add missing ? in an url, as we add parameters next
        url += '?'

    url = modify_url(url, queries, "of", "xm", True)
    url = modify_url(url, queries, "spc.sf", "dc.date.issued", True)
    url = modify_url(url, queries, "spc.sd", "DESC", False)

    if os.environ.get('SERVER_ENGINE', 'dspace') == 'dspace':
        return convert_url_for_dspace(url)
    else:
        # Ok, we are done here for invenio
        return url


def get_notices(options):
    if options['url'] == "":
        options['error'] = get_message('danger', _("Url field is empty"))
        return options

    groupsby_all = options['groupsby_all']
    groupsby_year = options['groupsby_year']
    groupsby_doc = options['groupsby_doc']

    options['group_title'] = 'TITLE' in groupsby_all
    options['subgroup_title'] = 'TITLE' in groupsby_year or 'TITLE' in groupsby_doc

    # validate url
    url = validate_url(options['url'])

    # get notices
    notices = import_marc21xml(url)

    # check errors
    # FIXME: use exception to manage errors
    if notices and notices[0].get('message', '') != '':
        options['error'] = notices[0]
        notices = ''
    else:
        options['error'] = ''

    notices_length = len(notices)

    # second groupby firstly
    if 'DOC' in groupsby_doc:
        notices = get_sorted_by_doc_types(notices)

    # first groupby secondly
    if 'DOC' in groupsby_all:
        notices = get_sorted_by_doc_types(notices)
    else:
        notices = get_sorted_by_year(notices, url)

    # set groups
    if 'DOC' in groupsby_all:
        notices = get_groups(options, notices, 'Doc_Type', 'Publication_Year')
    else:
        notices = get_groups(options, notices, 'Publication_Year', 'Doc_Type')

    # add counter (for bullet numbering)
    setbullets(notices, options['bullet'], notices_length)

    # ordered records
    options['marc21xml'] = notices

    return options
