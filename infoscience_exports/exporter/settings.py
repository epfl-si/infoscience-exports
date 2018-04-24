import datetime

try:
    basestring
except NameError:
    basestring = str


##########################################
#
# Exporter Settings classes
#
##########################################
class ExporterSettings(object):
    pass


class ExporterBadSettings(Exception):
    pass


##########################################
# Renders specific settings
##########################################
class BasketSettings(ExporterSettings):
    def __init__(self, basket_id=None):
        self.basket_id = basket_id

    def to_post_dict(self):
        post_dict = {}
        if self.basket_id:
            post_dict['search_basket_id'] = self.basket_id
        return post_dict


class SearchSettings(ExporterSettings):
    def __init__(self,
                 pattern='',
                 field_restriction='',
                 collection='Infoscience/Research',
                 filter=None):

        self.pattern = pattern
        self.field_restriction = field_restriction

        if collection and collection.find(',') != -1:
            self.collection = collection.split(',')
        else:
            self.collection = collection

        self.filter = filter

    def get_cleaned_search_filter(self):
        search_filter = self.filter

        if search_filter:
            if isinstance(search_filter, basestring):
                search_filter = search_filter.split(',')

            # filter only in ASCII pls
            search_filter = map(
                lambda element: element.encode('utf8') if isinstance(element,
                                                                     unicode) else element,
                search_filter)

        return search_filter

    def to_post_dict(self):
        post_dict = {}
        if self.pattern:
            post_dict['search_pattern'] = self.pattern
        if self.field_restriction:
            post_dict['search_field_restriction'] = self.field_restriction
        if self.collection:
            post_dict['search_collection'] = self.collection
        if self.filter:
            post_dict['search_filter'] = ','.join(self.filter)
        return post_dict


##########################################
# Format 
##########################################
class FormatSettings(ExporterSettings):
    format_shortcuts_name = {
        'short': 'SHRT',
        'short_titles': 'SHTI',
        'short_authors': 'SHAU',
        'short_titles_authors': 'SHTIAU',
        'detailed': 'DTLD',
        'detailed_titles': 'DTTI',
        'detailed_authors': 'DTAU',
        'detailed_titles_authors': 'DTTIAU',
        'full': 'FULL',
        'full_authors': 'FLAU',
        'full_titles': 'FLTI',
        'full_titles_authors': 'FLTIAU',
    }

    def __init__(self,
                 format_name='short',
                 language='en',
                 bullets_type=None,
                 bullets_order='desc',
                 bullets_text="",
                 has_clickable_authors=False,
                 has_clickable_titles=False):

        self.language = language
        self.bullets_type = bullets_type
        self.bullets_order = bullets_order
        if bullets_text:
            self.bullets_text = bullets_text
        else:
            self.bullets_text = ""

        # check default format first
        if self.format_shortcuts_name.get(format_name):
            # Define format_code
            if has_clickable_titles:
                format_name += "_titles"

            if has_clickable_authors:
                format_name += "_authors"

            self.format_code = self.format_shortcuts_name[format_name]
            self.format_name = format_name
        # look at the others
        elif self.__is_this_format_in_invenio(format_name):
            self.format_code = format_name
            self.format_name = format_name
        else:
            # nothing found, use default
            self.format_code = self.format_shortcuts_name.get('detailed')
            self.format_name = 'detailed'

    def to_post_dict(self):
        post_dict = {}
        format_options = self.format_name.split('_')
        post_dict['format_type'] = format_options[0]
        for option in format_options:
            if option == 'titles':
                post_dict[
                    'link_has_clickable_titles'] = 'link_has_clickable_titles'
            elif option == 'authors':
                post_dict[
                    'link_has_clickable_authors'] = 'link_has_clickable_authors'

        if self.bullets_type:
            post_dict['format_bullets'] = 'format_bullets'
            post_dict['format_bullets_type'] = self.bullets_type
        if self.bullets_order:
            post_dict['format_bullet_order'] = self.bullets_order
        if self.bullets_text:
            post_dict['format_bullet_text'] = self.bullets_text
        return post_dict

    def __is_this_format_in_invenio(self, format_name):
        return
        # formats_list = get_output_formats(with_attributes=True)
        # formats_dicts = [value['attrs']['code'] for (format, value) in formats_list.items()]
        # return format_name in formats_dicts


##########################################
# Filter 
##########################################        
class FilterSettings(ExporterSettings):
    """
    Arguments : 
        published : range or date
        published_date : if published == 'range', then this is the range
        published_from : all or yyyy
        published_to : present or yyyy
    """

    def __init__(self, published='range', published_from='all',
                 published_to='present', published_date='current'):
        self.published = published
        self.published_date = published_date

        self.date_min = 1950
        self.date_max = datetime.datetime.now().year

        self.published_from = published_from
        self.published_to = published_to

        self.__define_min_max()

    def __define_min_max(self):
        try:
            if self.published == 'date':
                if self.published_date == 'current':
                    self.date_min = self.date_max
                else:
                    self.date_min = self.date_max - (
                    int(self.published_date) - 1)

            elif self.published == 'range':
                if self.published_from != 'all':
                    self.date_min = int(self.published_from)
                if self.published_to == 'present':
                    # keep some margin for futur publications
                    self.date_max = self.date_max + 10
                else:
                    self.date_max = int(self.published_to)
        except TypeError:
            self.published = 'range'
            self.published_from = 'all'
            self.published_to = 'present'

    def to_post_dict(self):
        post_dict = {}
        if self.published:
            post_dict['filter_published'] = self.published
        if self.published_from:
            post_dict['filter_published_from'] = self.published_from
        if self.published_to:
            post_dict['filter_published_to'] = self.published_to
        return post_dict

    def get_published_from(self):
        return self.date_min

    def get_published_to(self):
        return self.date_max

    def get_for_pattern_years_string(self):
        year_pattern = []
        nb_i = self.date_max - self.date_min
        i = 0

        while True:
            year_pattern.append("year:%i" % (self.date_max - i))
            i += 1
            if i > nb_i:
                break

        # if the want everything, add no dates publications
        if self.published_from == 'all' and self.published == 'range':
            return ''

        if year_pattern:
            if len(year_pattern) > 1:
                return " (" + " or ".join(year_pattern) + ")"
            else:
                return " " + year_pattern[0]
        else:
            return ""


##########################################
# Links
##########################################
class LinkSettings(ExporterSettings):
    def __init__(self,
                 has_readable_links=False,
                 bibtex=None,
                 detailed_record=None,
                 endnote=None,
                 fulltext=None,
                 official=None,
                 export_id_in_comment=0,
                 target_langage=None):
        self.post = {}

        # if not 0, add in the export a html comment with a link to the curator view
        self.export_id_in_comment = export_id_in_comment

        if has_readable_links:
            self.post['link_has_readable_links'] = 'link_has_readable_links'
        if bibtex:
            self.post['link_has_bibtex'] = 'link_has_detailed_record'
            self.post['link_text_bibtex'] = bibtex
        if detailed_record:
            self.post['link_has_detailed_record'] = 'link_has_detailed_record'
            self.post['link_text_detailed_record'] = detailed_record
        if endnote:
            self.post['link_has_endnote'] = 'link_has_detailed_record'
            self.post['link_text_endnote'] = endnote
        if fulltext:
            self.post['link_has_fulltext'] = 'link_has_detailed_record'
            self.post['link_text_fulltext'] = fulltext
        if official:
            self.post['link_has_official'] = 'link_has_detailed_record'
            self.post['link_text_official'] = official
        if target_langage:
            self.post['link_target_langage'] = target_langage

        if bibtex or detailed_record or endnote or fulltext or official:
            self.need_link = True
            if target_langage:
                self.__detailed_record_href = '/record/%(record_id)s?ln=' + target_langage
            else:
                self.__detailed_record_href = '/record/%(record_id)s'

            self.__fulltext_href = '%(fulltext_url)s'
            self.__official_href = 'http://dx.doi.org/%(doi)s'
            self.__bibtex_href = '/curator/convert/bibtex?p=recid:%(record_id)s'
            self.__endnote_href = '/curator/convert/endnote?p=recid:%(record_id)s'
            self.__readable_tag = '<div class="readable_link">%s : %s</div>'
            self.__link_tag = '<a href="%s" class="%s">%s</a>'
            self.__join_string = ""

            if has_readable_links:
                if fulltext:
                    href = self.__fulltext_href
                    self.fulltext = self.__readable_tag % (fulltext, href)
                else:
                    self.fulltext = ''

                if official:
                    href = self.__official_href
                    self.official = self.__readable_tag % (official, href)
                else:
                    self.official = ''

                if endnote:
                    href = self.__endnote_href
                    self.endnote = self.__readable_tag % (endnote, href)
                else:
                    self.endnote = ''

                if detailed_record:
                    href = self.__detailed_record_href
                    self.detailed_record = self.__readable_tag % (
                    detailed_record, href)
                else:
                    self.detailed_record = ''

                if bibtex:
                    href = self.__bibtex_href
                    self.bibtex = self.__readable_tag % (bibtex, href)
                else:
                    self.bibtex = ''
            else:
                self.__join_string = " - "

                if fulltext:
                    href = self.__fulltext_href
                    self.fulltext = self.__link_tag % (
                    href, "infoscience_link_fulltext", fulltext)
                else:
                    self.fulltext = ''

                if official:
                    href = self.__official_href
                    self.official = self.__link_tag % (
                    href, "infoscience_link_official", official)
                else:
                    self.official = ''

                if endnote:
                    href = self.__endnote_href
                    self.endnote = self.__link_tag % (
                    href, "infoscience_link_endnote", endnote)
                else:
                    self.endnote = ''

                if detailed_record:
                    href = self.__detailed_record_href
                    self.detailed_record = self.__link_tag % (
                    href, "infoscience_link_detailed", detailed_record)
                else:
                    self.detailed_record = ''

                if bibtex:
                    href = self.__bibtex_href
                    self.bibtex = self.__link_tag % (
                    href, "infoscience_link_bibtex", bibtex)
                else:
                    self.bibtex = ''
        else:
            self.need_link = False

    def to_post_dict(self):
        return self.post

    def _get_fulltext_link(self, recid):
        return

    def render(self, record_id, doi=None):
        if not self.need_link:
            return ""

        rendered_links = []

        rendered_links.append(self.detailed_record % {'record_id': record_id})

        fulltext_link = self._get_fulltext_link(record_id)

        if fulltext_link:
            rendered_links.append(
                self.fulltext % {'fulltext_url': fulltext_link})

        if doi:
            rendered_links.append(self.official % {'doi': doi.decode('utf-8')})

        rendered_links.append(self.bibtex % {'record_id': record_id})

        rendered_links.append(self.endnote % {'record_id': record_id})

        return '<p class="infoscience_links">%s</p>' % self.__join_string.join(
            filter(lambda x: x, rendered_links))


##########################################
# Group by
##########################################
class GroupBySettings(ExporterSettings):
    """
    Set how the datas are grouped and which levels
    are showed
    """

    def __init__(self,
                 first='year',
                 second=None,
                 year_display_headings=False,
                 year_order='desc',
                 year_seperate_pending=False,
                 doctype_display_headings=False,
                 doctype_order=None):
        if first:
            if first != 'year' and first != 'doctype':
                raise ExporterBadSettings()

        if second:
            if second != 'year' and second != 'doctype':
                raise ExporterBadSettings()

        self.first = first
        self.second = second

        self.year_display_headings = year_display_headings
        self.year_order = year_order
        self.year_seperate_pending = year_seperate_pending
        self.doctype_display_headings = doctype_display_headings

        self._set_level_visibility()

        self.doctype_order = doctype_order

    def _set_level_visibility(self):
        # manage level visibility
        self.show_first_level = False
        self.show_second_level = False
        # do we need to show the first level?
        if (self.first == 'year' and self.year_display_headings) \
                or (self.first == 'doctype' and self.doctype_display_headings):
            self.show_first_level = True

        # and the second ?
        if (self.first == 'year' and self.second \
                    and self.doctype_display_headings) or \
                (self.first == 'doctype' and self.second \
                         and self.year_display_headings):
            self.show_second_level = True

    def to_post_dict(self):
        post_dict = {}
        if self.first:
            post_dict['group_by_first'] = self.first
        if self.second:
            post_dict['group_by_second'] = self.second
        if self.year_display_headings:
            post_dict[
                'group_by_year_display_headings'] = 'group_by_year_display_headings'
        if self.year_order:
            post_dict['group_by_year_order'] = self.year_order
        if self.year_seperate_pending:
            post_dict[
                'group_by_year_seperate_pending'] = 'group_by_year_seperate_pending'
        if self.doctype_display_headings:
            post_dict[
                'group_by_doctype_display_headings'] = 'group_by_doctype_display_headings'
        if self.doctype_order:
            post_dict['group_by_ordered_doctype_list'] = ','.join(
                self.doctype_order)
        return post_dict
