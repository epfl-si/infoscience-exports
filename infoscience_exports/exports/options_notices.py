from django.utils.translation import ugettext_lazy as _

from itertools import groupby
from operator import itemgetter

from .marc21xml import import_marc21xml


DOC_TYPE_ORDERED = (
    ('ARTICLE', _("Journal Articles")),
    ('CONF', _("Conference Papers")),
    ('REVIEW', _("Reviews")),
    ('BOOK', _("Books")),
    ('THESIS', _("PhD Theses")),
    ('EPFLTHESIS', _("EPFL PhD Theses")),
    ('CHAPTER', _("Book Chapters")),
    ('PROC', _("Conference Proceedings")),
    ('WORKING', _("Working Papers")),
    ('REPORT', _("Technical Reports")),
    ('POSTER', _("Posters")),
    ('TALK', _("Presentations")),
    ('STANDARD', _("Standards")),
    ('PATENT', _("Patents")),
    ('STUDENT', _("Student works")),
    ('POLY', _("Teaching Documents")),
    ('FILM', _("")),
    ('MAP', _("")),
    ('PHOTO', _("")),
    ('DIGIT', _("")),
    ('UNKOWN', _("")),
)


def get_groups(options, notices, attr, subattr):
    doc_type = dict(DOC_TYPE_ORDERED)
    groups_list = []
    for key, items in groupby(notices, itemgetter(attr)):
        subgroups_list = []
        for subkey, subitems in groupby(items, itemgetter(subattr)):
            list2 = [{'title': doc_type[subkey[0]]}] if subattr == 'Doc_Type' else [{'title': subkey}]
            list2.extend(list(subitems))
            subgroups_list.append(list2)
        list1 = [{'title': doc_type[key[0]]}] if attr == 'Doc_Type' else [{'title': key}]
        list1.extend(list(subgroups_list))
        groups_list.append(list1)
    return groups_list


def get_sorted_by_year(notices, groups):
    if 'ASC' in groups:
        notices = sorted(notices, key=lambda k: k['Publisher_Date'])
    elif 'DESC' in groups:
        notices = sorted(notices, key=lambda k: k['Publisher_Date'], reverse=True)
    return notices


def get_sorted_by_doc_types(notices):
    notices = sorted(notices, key=lambda k: (k['Doc_Type']))
    groups_list = []
    groups_head = []
    for key, items in groupby(notices, itemgetter('Doc_Type')):
        groups_list.append(list(items))
        groups_head.append(key)
    groups_list_ordered = []
    for doc_type in DOC_TYPE_ORDERED:
        index = 0 
        for head in groups_head:
            if head[0] == doc_type[0]:
                 groups_list_ordered.extend(groups_list[index])
            index += 1
    return groups_list_ordered   


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
    groupsby_all = options['groupsby_all']
    groupsby_year = options['groupsby_year']
    groupsby_doc = options['groupsby_doc']

    options['group_title'] = 'TITLE' in groupsby_all
    options['subgroup_title'] = 'TITLE' in groupsby_year or 'TITLE' in groupsby_doc

    notices = import_marc21xml(options['url']) if options['url'] else ''

    notices_length = len(notices)

    # remove pending publications if not needed
    if 'PUBL' not in groupsby_all and 'PUBL' not in groupsby_year and 'PUBL' not in groupsby_doc:
        pass

    # second groupby firstly
    if 'YEAR' in groupsby_year:
        notices = get_sorted_by_year(notices, groupsby_year)
    elif 'DOC' in groupsby_doc:
        notices = get_sorted_by_doc_types(notices)

    # first groupby secondly
    if 'YEAR' in groupsby_all:
        notices = get_sorted_by_year(notices, groupsby_all)
    elif 'DOC' in groupsby_all:
        notices = get_sorted_by_doc_types(notices)

    # set groups
    if 'YEAR' in groupsby_all:
        notices = get_groups(options, notices, 'Publisher_Date', 'Doc_Type')
    elif 'DOC' in groupsby_all:
        notices = get_groups(options, notices, 'Doc_Type', 'Publisher_Date')

    # add counter (for bullet numbering)
    setbullets(notices, options['bullet'], notices_length)
        

    options['marc21xml'] = notices

    return options
