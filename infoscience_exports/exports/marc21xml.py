# -*- coding: utf-8 -*-

"""
Example usage: python simpledump.py data/marc/010-lok.mrc
"""

from urllib.request import urlopen
from pymarc import marcxml
#import sys


def get_list(fields, name):
    result = []
    for element in fields:
        for key, value in element.items():
            value_to_append = value
            if key == name:
                if name == '013':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                    value_to_append += '(' + res_value['c'] + ')' if 'c' in res_value else ''
                elif name == '520':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                elif name == '700':
                    subfields = value['subfields']
                    res_value = {}
                    for element1 in subfields:
                        for key1, value1 in element1.items():
                            res_value[key1] = value1
                    value_to_append = res_value['a'] if 'a' in res_value else ''
                  
                result.append(value_to_append)
    return result
  
def parse_dict(record):
    result = {}
    fields = record['fields']
    result['control_number'] = get_list(fields, '001')[0]
    result['patent_control_information'] = get_list(fields, '013')
    result['summary'] = get_list(fields, '520')
    result['added_entry_personal_name'] = get_list(fields, '700')
    return result

def import_marc21xml(url):
    reader = marcxml.parse_xml_to_array(urlopen(url))
    result = []
    for record in reader:
        dict_result = {}
        dict_record = parse_dict(record.as_dict())
        dict_result['Id'] = dict_record['control_number']
        dict_result['Record'] = dict_record
        dict_result['Title'] = record.uniformtitle()
        dict_result['Title_All'] = record.title()
        dict_result['Authors'] = dict_record['added_entry_personal_name'] #[entry.format_field() for entry in record.addedentries()]
        dict_result['Author'] = record.author() if record.author() else ''
        dict_result['Patents'] = dict_record['patent_control_information']
        dict_result['Publisher'] = record.publisher() if record.publisher() else ''
        dict_result['Publisher_Date'] = record.pubyear() if record.pubyear() else ''
        dict_result['ISBN'] = record.isbn()
        dict_result['Description'] = [entry.format_field() for entry in record.physicaldescription()]
        dict_result['Summary'] = dict_record['summary'] #[entry.format_field() for entry in record.notes()]
        dict_result['Subjects'] = [entry.format_field() for entry in record.subjects()]
        result.append(dict_result)
    return result

