from logging import getLogger

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from urllib.parse import parse_qs, urlsplit
from itertools import groupby
from operator import itemgetter

from .marc21xml import import_marc21xml
from .messages import get_message

logger = getLogger(__name__)


DOC_TYPE_ORDERED = {
    # ('ARTICLE', _("Journal Articles")),
    'ARTICLE': _("Articles & Reviews"),
    'CONF': _("Conference Papers"),
    'REVIEW': _("Reviews"),
    'BOOK': _("Books"),
    'THESIS_LIB': _("PhD Theses"),
    'THESIS': _("EPFL PhD Theses"),
    'CHAPTER': _("Book Chapters"),
    'PROC': _("Conference Proceedings"),
    'WORKING': _("Working Papers"),
    'REPORT': _("Technical Reports"),
    'POSTER': _("Posters"),
    'TALK': _("Presentations"),
    'STANDARD': _("Standards"),
    'PATENT': _("Patents"),
    'STUDENT': _("Student works"),
    'POLY': _("Teaching Documents"),
    'REP_WORK': _("Report & Working papers"),
    'POST_TALK': _("Posters & Talks"),
    'BOOK_CHAP': _("Book chapters"),
    'FILM': _("Movies"),
    'MAP': _("Maps"),
    'PHOTO': _("Pictures"),
    'DIGIT': _("Digits"),
    'UNKOWN': _("Unkonwns"),
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


def validate_url(url):
    queries = parse_qs(urlsplit(url).query)

    url = modify_url(url, queries, "of", "xm", True)
    url = modify_url(url, queries, "sf", "year", True)
    url = modify_url(url, queries, "so", "d", False)

    if 'rg' in queries and queries['rg'][0] == '10':
        url = url.replace("rg=10", "rg=" + str(settings.RANGE_DISPLAY))
    elif '&rg=' not in url:
        url = url + "&rg=50"

    return url


def get_notices(options):
    if options['url'] == "":
        options['error'] = set_message('danger', _("Url field is empty"))
        return options

    groupsby_all = options['groupsby_all']
    groupsby_year = options['groupsby_year']
    groupsby_doc = options['groupsby_doc']

    options['group_title'] = 'TITLE' in groupsby_all
    options['subgroup_title'] = 'TITLE' in groupsby_year or 'TITLE' in groupsby_doc

    # remove pending publications if not needed
    can_display_pending_publications = options['pending_publications']

    # validate url
    url = validate_url(options['url'])

    # get notices
    notices = import_marc21xml(url, can_display_pending_publications)

    # check errors
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
