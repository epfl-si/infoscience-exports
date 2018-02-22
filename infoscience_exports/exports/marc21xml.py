# -*- coding: utf-8 -*-

"""
Example usage: python simpledump.py data/marc/010-lok.mrc
"""

from urllib.request import urlopen
from pymarc import marcxml
#import sys


def get_list(fields, code, subcode='', subcode2=''):
    result = []
    for element in fields:
        for key, value in element.items():
            value_to_append = value
            if key == code:
                if code == '013':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                    value_to_append += '(' + res_value['c'] + ')' if 'c' in res_value else ''
                elif code == '024':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    if len(subfields) == 2 and subcode in res_value and '2' in res_value and res_value['2'] == subcode2:
                        value_to_append = "http://dx.doi.org/" + res_value['a']
                    else:
                        value_to_append = ''
                elif code == '520':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                elif code == '700':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                elif code == '856':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['u'] if 'u' in res_value and 'x' in res_value and res_value['x'] == subcode else ''
                  
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
    return result


def get_authors_initials(authors):
    n = len(authors)
    n1 = n - 1
    i = 0
    result = ""
    for author in authors:
        names = author.split(',')
        family = names[0].strip() if len(names) > 0 else ''
        fnames = names[1].split(' ') if len(names) > 1 else ''
        for fname in fnames:
            if not fname:
                continue
            fname = fname.strip()
            if "-" in fname:
                snames = fname.split("-")
                if len(snames[0]) > 1:
                    result += snames[0][0] + "."
                if len(snames[0]) > 1 or len(snames[1]) > 1:
                    result += "-"
                if len(snames[1]) > 1:
                    result += snames[1][0] + ". "
            else:   
                fname = fname.strip()
                if len(fname) > 0:  
                    result += fname.strip()[0] + ". "
        if family:
            result += family
        
        i += 1
        if n == i:
            result += "."
        elif n1 == i:
            result += " and "
        else:
            result += ", "
    return result


def import_marc21xml(url):
    reader = marcxml.parse_xml_to_array(urlopen(url))
    result = []
    for record in reader:
        dict_result = {}
        dict_record = parse_dict(record.as_dict())
        dict_result['Id'] = dict_record['control_number']
        dict_result['ELA_Icon'] = dict_record['ela_icon'] # Electronic Location and Access
        dict_result['ELA_URL'] = dict_record['ela_url'] # Electronic Location and Access   
        dict_result['View_Publisher'] = dict_record['osi_doi'] # Other Standard Identifier - Digital Object Identifier   
        dict_result['Title'] = record.uniformtitle()
        dict_result['Title_All'] = record.title()
        dict_result['Authors'] = dict_record['added_entry_personal_name'] #[entry.format_field() for entry in record.addedentries()]
        dict_result['Author'] = record.author() if record.author() else ''
        dict_result['Authors_Initials'] = get_authors_initials(dict_result['Authors'])
        dict_result['Patents'] = dict_record['patent_control_information']
        dict_result['Publisher'] = record.publisher() if record.publisher() else ''
        dict_result['Publisher_Date'] = record.pubyear() if record.pubyear() else ''
        dict_result['ISBN'] = record.isbn()
        dict_result['Description'] = [entry.format_field() for entry in record.physicaldescription()]
        dict_result['Summary'] = dict_record['summary'] #[entry.format_field() for entry in record.notes()]
        dict_result['Subjects'] = [entry.format_field() for entry in record.subjects()]
        result.append(dict_result)
    return result

