from logging import getLogger
from urllib.request import urlopen

from django.utils.translation import gettext_lazy as _

import unicodedata
from urllib.parse import parse_qs, urlsplit
from itertools import groupby
from operator import itemgetter

from .marc21xml import import_marc21xml
from .messages import get_message
from .url_validator import DomainNotAllowedError, validate_url

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
    try:
        url = validate_url(options['url'])
        # Look like it serve to remove all non-spacing (invisible) Unicode
        url = ''.join(c for c in unicodedata.normalize('NFD', url) if unicodedata.category(c) != 'Mn')
        logger.debug(f"URL { url } passed the validation. Fetching the URL..")
    except DomainNotAllowedError:
        options['error'] = get_message('danger', _('The domain is not allowed'))
        return options
    except Exception as e:
        options['error'] = get_message('danger', e)
        return options

    # download data
    try:
        server_response = urlopen(url)
        logger.debug(f"URL opened successfully. HTTP code: { server_response.getcode() }")
    except Exception as e:
        options['error'] = get_message('danger', f"Server responded with an error: {e}")
        return options

    # get notices
    try:
        notices = import_marc21xml(server_response)
    except Exception as e:
        if str(e).startswith('<unknown>:'):
            options['error'] = get_message('danger', f"XML parse error: {e}")
            return options
        else:
            options['error'] = get_message('danger', e)
            return options

    # check errors inside parsed result
    if notices and notices[0].get('message', '') != '':
        options['error'] = notices[0]
        notices = ''
    else:
        options['error'] = ''

    notices_length = len(notices)

    logger.debug(f"Records successfully transformed from MarcXML to array. Length: { notices_length }")

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
