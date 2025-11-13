import os
from urllib.parse import parse_qs, urlsplit, urlparse

from django.conf import settings
from furl import furl

from exports.utils import is_valid_uuid


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

    is_a_direct_item_url = False

    try:
        # check if we are with a direct item url
        if len(f.path.segments) > 2 and \
                'entities' in f.path.segments:
            if is_valid_uuid(f.path.segments[2]):
                uuid = f.path.segments[2]
                # yes we are. Is that for a unit ?
                if 'orgunit' in f.path.segments[1]:  # convert any direct unit url
                    f.path = 'server/api/discover/export'
                    f.args['configuration'] = 'RELATION.OrgUnit.publications'
                    f.args['scope'] = uuid
                    is_a_direct_item_url = True
                elif 'person' in f.path.segments[1]:  # convert any direct person url
                    f.path = 'server/api/discover/export'
                    f.args['configuration'] = 'RELATION.Person.researchoutputs'
                    f.args['scope'] = uuid
                    is_a_direct_item_url = True
    except:  # skip url modification on any errors
        pass

    if not is_a_direct_item_url:
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

    # Safeguards part
    # do not allow empty query, as it may crash the server
    if (not is_a_direct_item_url and
            ('query' not in f.args or not f.args['query'])
    ):
        raise Exception("the URL provided has not the 'query' parameters")

    # hard limit or crash the server
    if settings.RANGE_DISPLAY and \
            'spc.rpp' in f.args and \
            f.args['spc.rpp'].isnumeric() and \
            int(f.args['spc.rpp']) > int(settings.RANGE_DISPLAY):
        f.args['spc.rpp'] = settings.RANGE_DISPLAY

    return f.url


class DomainNotAllowedError(Exception):
    """Raised when trying to access a domain that is not allowed"""
    pass


def validate_url(url):
    queries = parse_qs(urlsplit(url).query)

    if '?' not in url:
        # mandatory seperator for next parts
        url += '?'

    url = modify_url(url, queries, "of", "xm", True)
    url = modify_url(url, queries, "spc.page", "1", True)  # mandatory

    # There was a time when the sort field was forced to "dc.date.issued", as it may have been a need to
    # assert we get "the top x" (x being the limit) publications before doing custom group-by or sorts
    # Now we allow the sort to be defined by the user's provided Infoscience URL
    url = modify_url(url, queries, "spc.sf", "dc.date.issued", False)
    url = modify_url(url, queries, "spc.sd", "DESC", False)

    if os.environ.get('SERVER_ENGINE', 'dspace') == 'dspace':
        url = convert_url_for_dspace(url)

    o = urlparse(url)

    if '*' not in settings.ALLOWED_HOSTS and \
            o.netloc not in settings.ALLOWED_HOSTS:
        raise DomainNotAllowedError()

    # Don't welcome self-referencing urls
    if url.find(settings.SITE_DOMAIN + settings.SITE_PATH) != -1:
        raise DomainNotAllowedError()

    return url
