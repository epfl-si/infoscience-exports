# -*- coding: utf-8 -*-

"""
Parse a marc-21-xml file
"""
import re
from logging import getLogger
from django.utils.translation import gettext as _
from django.conf import settings
from os.path import dirname, splitext
from urllib.parse import urlparse
from urllib.request import urlopen
from pymarc import marcxml
import unicodedata

from .messages import get_message

logger = getLogger(__name__)


class Author:

    def __init__(self, author):
        self.fullname = author
        self.search_url = "{}/search?p={}".format(
            settings.SITE_DOMAIN, author.replace(",", "+").replace(" ", "+"))
        self.initname = self.compute_name()

    def compute_name(self):
        names = self.fullname.split(',')
        family = names[0].strip() if len(names) > 0 else ''
        fnames = names[1].split(' ') if len(names) > 1 else ''

        initname = ""
        for fname in fnames:
            if not fname:
                continue
            fname = fname.strip()
            if "-" in fname:
                snames = fname.split("-")
                if len(snames[0]) > 1:
                    initname += snames[0][0] + "."
                if len(snames[0]) > 1 or len(snames[1]) > 1:
                    initname += "-"
                if len(snames[1]) > 1:
                    initname += snames[1][0] + ". "
            else:
                fname = fname.strip()
                if len(fname) > 0:
                    initname += fname.strip()[0] + ". "
        if family:
            initname += family

        return initname


# Authors is a list of Author instance: full name, initial name, url in infoscience
def set_authors(authors):
    return [Author(author) for author in authors]


# get only the year in a date-string
def set_year(date):
    dates = [val for val in date.split("-") if len(val) == 4]
    if len(dates) == 1:
        return dates[0]
    else:
        logger.warning("Year not found in %s, decomposed as %s", date, dates)
        return ''


def set_fulltext(fulltexts):
    """ get fulltext: link to pdf or link to repository if several links """
    # only keep pdfs and remove duplicates
    file_paths = ['{}://{}{}'.format(*urlparse(fulltext)[:3]) for fulltext in fulltexts]
    pdfs = [pdf for pdf in file_paths if splitext(pdf)[1] == '.pdf']
    unic_pdfs = list(set(pdfs))

    # return empty string if no pdf found
    if len(unic_pdfs) == 0:
        return ''

    # return element if only one found
    if len(unic_pdfs) == 1:
        return unic_pdfs[0]

    # multiple pdfs found... return first folder that matchs infoscience/record/xxx/files
    for dir_path in map(dirname, unic_pdfs):
        if re.search("infoscience.epfl.ch/record/\d+/files", dir_path):
            return dir_path

    # no infoscience folder found... log a warning and return first match
    logger.warning("Multiple pdfs found (%s), but none appear to be on regular infoscience path", unic_pdfs)
    return dirname(unic_pdfs[0])


def get_attributes(subfields):
    res_value = {}
    for element1 in subfields:
        for key1, value1 in element1.items():
            res_value[key1] = value1
    return res_value


# get dictionary (icon, fulltexts) of ELA
def get_ELA_fields(field):
    ela_fulltexts = []
    ela_icon = ''
    for ela in field:
        ELA_object = ela.get('u', '').lower()
        if ELA_object.endswith(".pdf"):
            ela_fulltexts.append(ela.get('u', ''))
        elif ELA_object.endswith(".png") or ELA_object.endswith(".jpg"):
            ela_icon = ela.get('u', '')
    ela_fulltexts = list(filter(None, ela_fulltexts))
    ela_fulltexts = set_fulltext(ela_fulltexts)
    return {'icon': ela_icon, 'fulltexts': ela_fulltexts}


# parser for xml file
def get_list(fields, code, ind1, ind2, subcodes):
    result = []
    for field in fields:
        for key, value in field.items():
            if key == code:
                if code < '010':  # controlfield
                    result.append(value)
                elif value['ind1'] == ind1 and value['ind2'] == ind2:  # datafield
                    res_value = get_attributes(value['subfields'])
                    value_to_append = {}
                    for subcode in subcodes:
                        value_to_append[subcode] = res_value.get(subcode, '')
                    result.append(value_to_append)
    result = list(filter(None, result))
    return result


def get_dict(field):
    return field[0] if field else {}


def get_values(field_list, subcode):
    result = []
    for field in field_list:
        result.append(field[subcode])
    return result


def get_value(field_list, subcode):
    return field_list[0][subcode] if field_list else ''


def parse_dict(record):
    result = {}
    fields = record['fields']

    # '001', ' ', ' ', []
    result['control_number'] = get_list(fields, '001', ' ', ' ', [])[0]

    # '013', ' ', ' ', ['a', 'c']
    result['patent_control_information'] = get_list(fields, '013', ' ', ' ', ['a', 'c'])

    # '020', ' ', ' ', ['a']
    isbn = get_list(fields, '020', ' ', ' ', ['a'])
    result['isbn'] = get_value(isbn, 'a')

    # '024', '7', ' ', ['a']      => Other Standard Identifier: Digital Object Identifier
    other_standard_identification_doi = get_list(fields, '024', '7', ' ', ['a'])
    result['other_standard_identification_doi'] = get_value(other_standard_identification_doi, 'a')

    # '245', ' ', ' ', ['a']
    title = get_list(fields, '245', ' ', ' ', ['a'])
    result['title'] = get_value(title, 'a')

    # '260', ' ', ' ', ['a', 'b']
    publication_distribution = get_list(fields, '260', ' ', ' ', ['a', 'b'])
    result['publication_distribution'] = get_dict(publication_distribution)

    # '269', ' ', ' ', ['a']
    date_of_publication = get_list(fields, '269', ' ', ' ', ['a'])
    result['date_of_publication'] = get_value(date_of_publication, 'a')

    # '300', ' ', ' ', ['a']
    physical_description_extent = get_list(fields, '300', ' ', ' ', ['a'])
    result['physical_description_extent'] = get_value(physical_description_extent, 'a')

    # '336', ' ', ' ', ['a']
    source_of_acquisition = get_list(fields, '336', ' ', ' ', ['a'])
    result['source_of_acquisition'] = get_value(source_of_acquisition, 'a')

    # '520', ' ', ' ', ['a']
    summary = get_list(fields, '520', ' ', ' ', ['a'])
    result['summary'] = get_value(summary, 'a')

    # '700', ' ', ' ', ['a']
    added_entry_personal_name = get_list(fields, '700', ' ', ' ', ['a'])
    authors = get_values(added_entry_personal_name, 'a')
    result['added_entry_personal_name'] = set_authors(authors)

    # '710', ' ', ' ', ['a']
    added_entry_corporate_name = get_list(fields, '710', ' ', ' ', ['a'])
    result['added_entry_corporate_name'] = get_values(added_entry_corporate_name, 'a')

    # '711', ' ', ' ', ['a', 'c', 'd']
    added_entry_meeting = get_list(fields, '711', ' ', ' ', ['a', 'c', 'd'])
    if not added_entry_meeting:
        added_entry_meeting = get_list(fields, '711', '2', ' ', ['a', 'c', 'd'])
    result['added_entry_meeting'] = get_dict(added_entry_meeting)

    # '720', ' ', '1', ['a']
    added_entry_uncontrolled_name_person = get_list(fields, '720', ' ', '1', ['a'])
    authors = get_values(added_entry_uncontrolled_name_person, 'a')
    result['added_entry_uncontrolled_name_person_1'] = set_authors(authors)

    # '720', ' ', '2', ['a']
    added_entry_uncontrolled_name_person = get_list(fields, '720', ' ', '2', ['a'])
    authors = get_values(added_entry_uncontrolled_name_person, 'a')
    result['added_entry_uncontrolled_name_person_2'] = set_authors(authors)

    # '720', ' ', '3', ['a']
    added_entry_uncontrolled_name_person = get_list(fields, '720', ' ', '3', ['a'])
    authors = get_values(added_entry_uncontrolled_name_person, 'a')
    result['added_entry_uncontrolled_name_person_3'] = set_authors(authors)

    # '720', ' ', '5', ['a']
    added_entry_uncontrolled_name_company = get_list(fields, '720', ' ', '5', ['a'])
    result['added_entry_uncontrolled_name_company'] = get_value(added_entry_uncontrolled_name_company, 'a')

    # '773', ' ', ' ', ['j', 'k', 'q', 't']
    journal = get_list(fields, '773', ' ', ' ', ['j', 'k', 'q', 't'])
    result['host_item_entry'] = get_dict(journal)

    # '790', ' ', ' ', ['w']
    local_added_entry_url_link = get_list(fields, '790', ' ', ' ', ['w'])
    result['local_added_entry_url_link'] = get_value(local_added_entry_url_link, 'w')

    # '856', '4', ' ', ['u']      => Electronic Location Access: Icon url, links to Full Texts
    electronic_location_access = get_list(fields, '856', '4', ' ', ['u'])
    result['electronic_location_access'] = get_ELA_fields(electronic_location_access)

    # '909', 'C', '0', ['p']
    approved_publications = get_list(fields, '909', 'C', '0', ['p'])
    result['approved_publications'] = get_values(approved_publications, 'p')

    # '999', 'C', '0', ['p']
    pending_publications = get_list(fields, '999', 'C', '0', ['p'])
    result['pending_publications'] = get_values(pending_publications, 'p')

    return result


def import_marc21xml(url, can_display_pending_publications):
    result = []

    o = urlparse(url)
    if '*' not in settings.ALLOWED_HOSTS and \
            o.netloc not in settings.ALLOWED_HOSTS:
        result.append(get_message('danger', _('The domain is not allowed')))
        return result

    try:
        url = ''.join(c for c in unicodedata.normalize('NFD', url) if unicodedata.category(c) != 'Mn')
        reader = marcxml.parse_xml_to_array(urlopen(url))
    except IOError as e:
        result.append(get_message('danger', str(e)))
    except Exception as e:
        result.append(get_message('danger', str(e)))
    if result:
        return result

    for record in reader:
        dict_result = {}
        dict_record = parse_dict(record.as_dict())
        dict_result['Id'] = dict_record['control_number']
        dict_result['Infoscience_URL'] = "{}/record/{}".format(
            settings.SITE_DOMAIN, dict_record['control_number'])
        dict_result['ELA_Icon'] = dict_record['electronic_location_access']['icon']
        dict_result['ELA_URL'] = dict_record['electronic_location_access']['fulltexts']
        dict_result['DOI'] = dict_record['other_standard_identification_doi']
        dict_result['Title'] = dict_record['title']
        dict_result['Authors'] = dict_record['added_entry_personal_name']
        dict_result['Authors_1'] = dict_record['added_entry_uncontrolled_name_person_1']
        dict_result['Authors_3'] = dict_record['added_entry_uncontrolled_name_person_3']
        dict_result['Directors'] = dict_record['added_entry_uncontrolled_name_person_2']
        dict_result['Patents'] = dict_record['patent_control_information']
        dict_result['Publication_Location'] = dict_record['publication_distribution'].get('a', '')
        dict_result['Publication_Institution'] = dict_record['publication_distribution'].get('b', '')
        dict_result['Publication_Date'] = dict_record['date_of_publication']
        dict_result['Publication_Year'] = set_year(dict_result['Publication_Date'])
        dict_result['Publication_Pages'] = dict_record['physical_description_extent']
        dict_result['Publisher'] = dict_record['host_item_entry'].get('t', '')
        dict_result['Publisher_Volume'] = dict_record['host_item_entry'].get('j', '')
        dict_result['Publisher_Volume_Number'] = dict_record['host_item_entry'].get('k', '')
        dict_result['Publisher_Volume_Pages'] = dict_record['host_item_entry'].get('q', '')
        dict_result['Local_Url_Link'] = dict_record['local_added_entry_url_link']
        dict_result['Conference_Meeting_Name'] = dict_record['added_entry_meeting'].get('a', '')
        dict_result['Conference_Meeting_Location'] = dict_record['added_entry_meeting'].get('c', '')
        dict_result['Conference_Meeting_Date'] = dict_record['added_entry_meeting'].get('d', '')
        dict_result['Corporate_Name'] = dict_record['added_entry_corporate_name']
        dict_result['Company_Name'] = dict_record['added_entry_uncontrolled_name_company']
        dict_result['Approved_Publications'] = dict_record['approved_publications']
        dict_result['Pending_Publications'] = dict_record['pending_publications']
        dict_result['Doc_Type'] = dict_record['source_of_acquisition']
        dict_result['ISBN'] = dict_record['isbn']
        dict_result['Summary'] = dict_record['summary']

        dict_result['Description'] = [entry.format_field() for entry in record.physicaldescription()]
        dict_result['Subjects'] = [entry.format_field() for entry in record.subjects()]

        is_pending = dict_result['Pending_Publications'] and not dict_result['Approved_Publications']
        if not is_pending or can_display_pending_publications:
            result.append(dict_result)

    if len(result) == 0 and len(reader) > 0:
        result.append(get_message('info', _('There are only pending publications')))

    return result
