# -*- coding: utf-8 -*-

"""
Parse a marc-21-xml file
"""

from django.utils.translation import gettext as _
from django.conf import settings
from urllib.parse import urlparse
from urllib.request import urlopen
from pymarc import marcxml


def get_attributes(subfields):
    res_value = {}
    for element1 in subfields:
        for key1, value1 in element1.items():
            res_value[key1] = value1
    return res_value


def get_list(fields, code, subcode='', subcode2=''):
    result = []
    for element in fields:
        for key, value in element.items():
            value_to_append = value
            if key == code:
                if code == '013':
                    res_value = get_attributes(value['subfields'])
                    value_to_append = res_value.get('a', '')
                    value_to_append += '(' + res_value['c'] + ')' if 'c' in res_value else ''
                elif code == '024':
                    res_value = get_attributes(value['subfields'])
                    if value['ind1'] == '7' \
                            and subcode in res_value \
                            and '2' in res_value \
                            and res_value['2'] == subcode2:
                        value_to_append = "http://dx.doi.org/" + res_value['a']
                    else:
                        value_to_append = ''
                elif code == '520':
                    res_value = get_attributes(value['subfields'])
                    value_to_append = res_value.get('a', '')
                elif code == '700':
                    res_value = get_attributes(value['subfields'])
                    value_to_append = res_value.get('a', '')
                elif code == '856':
                    res_value = get_attributes(value['subfields'])
                    value_to_append = res_value['u'] if 'u' in res_value \
                        and 'x' in res_value \
                        and res_value['x'] == subcode else ''
                elif code == '909':
                    if value['ind1'] == 'C' and value['ind2'] == '0':
                        res_value = get_attributes(value['subfields'])
                        value_to_append = res_value.get('p', '')
                elif code == '980':
                    subfields = value['subfields']
                    res_value = get_attributes(subfields)
                    value_to_append = res_value.get('a', '')
                elif code == '999':
                    if value['ind1'] == 'C' and value['ind2'] == '0':
                        res_value = get_attributes(value['subfields'])
                        value_to_append = res_value.get('p', '')

                result.append(value_to_append)

    result = list(filter(None, result))
    return result


def parse_dict(record):
    result = {}
    fields = record['fields']
    result['control_number'] = get_list(fields, '001')[0]
    result['patent_control_information'] = get_list(fields, '013')
    result['osi_doi'] = get_list(fields, '024', 'a', 'doi')
    result['summary'] = get_list(fields, '520')
    result['added_entry_personal_name'] = get_list(fields, '700')
    result['ela_icon'] = get_list(fields, '856', 'ICON')
    result['ela_url'] = get_list(fields, '856', 'PUBLIC')
    result['doc_type'] = get_list(fields, '980')
    result['approved_publications'] = get_list(fields, '909')
    result['pending_publications'] = get_list(fields, '999')
    return result


# Authors is a list of a dictionary of author: full name, initial name, url in infoscience
def set_authors(authors):
    result = []
    for author in authors:
        author_record = {}
        author_record['fullname'] = author
        author_record['url'] = author.replace(",", "+").replace(" ", "+")

        names = author.split(',')
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

        author_record['initname'] = initname
        result.append(author_record)

    return result


def set_year(date):
    if len(date) == 4:
        return date
    dates = date.split("-")
    year = date
    for val in dates:
        if len(val) == 4:
            year = val
            break
    return year


def import_marc21xml(url, can_display_pending_publications):
    result = []

    o = urlparse(url)
#    if o.netloc not in settings.ALLOWED_HOST:
#        result.append({'error': _('The domain is not allowed')})
#        return result

    try:
        reader = marcxml.parse_xml_to_array(urlopen(url))
    except IOError as e:
        result.append({'error': str(e)})
    except Exception as e:
        result.append({'error': str(e)})
    if result:
        return result
    
    pending_counter = 0
    for record in reader:
        dict_result = {}
        dict_record = parse_dict(record.as_dict())
        dict_result['Id'] = dict_record['control_number']
        dict_result['ELA_Icon'] = dict_record['ela_icon']  # Electronic Location and Access
        dict_result['ELA_URL'] = dict_record['ela_url']  # Electronic Location and Access
        dict_result['View_Publisher'] = dict_record['osi_doi']  # Other Standard Identifier - Digital Object Identifier
        dict_result['Title'] = record.uniformtitle()
        dict_result['Title_All'] = record.title()
        dict_result['Author'] = record.author() if record.author() else ''
        authors = dict_record['added_entry_personal_name']  # [entry.format_field() for entry in record.addedentries()]
        dict_result['Authors'] = set_authors(authors)
        dict_result['Patents'] = dict_record['patent_control_information']
        dict_result['Publisher'] = record.publisher() if record.publisher() else ''
        dict_result['Publisher_Date'] = record.pubyear() if record.pubyear() else ''
        dict_result['Publisher_Year'] = set_year(dict_result['Publisher_Date'])
        dict_result['Approved_Publications'] = dict_record['approved_publications']
        dict_result['Pending_Publications'] = dict_record['pending_publications']
        dict_result['Doc_Type'] = dict_record['doc_type']
        dict_result['ISBN'] = record.isbn()
        dict_result['Description'] = [entry.format_field() for entry in record.physicaldescription()]
        dict_result['Summary'] = dict_record['summary'][0] if dict_record['summary'] else ''  # [entry.format_field() for entry in record.notes()]
        dict_result['Subjects'] = [entry.format_field() for entry in record.subjects()]

        is_pending = dict_result['Pending_Publications'] and not dict_result['Approved_Publications']
        if not is_pending or can_display_pending_publications:
            result.append(dict_result)
        else:
            pending_counter += 1

    if pending_counter == len(reader):
        result.append({'error': _('Only pending publications')})

    return result
