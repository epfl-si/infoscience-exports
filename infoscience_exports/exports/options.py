# Some utilities about the options


def get_options_from_export_attributes(obj):
    # build an option dict defining the transformation of the notices
    return {
        'is_extern': True,
        'url': obj.url,
        'format': obj.formats_type,
        'bullet': obj.bullets_type,
        'thumb': obj.show_thumbnail,
        'summary': obj.show_summary,
        'link_authors': obj.show_linkable_authors,
        'link_print': obj.show_links_for_printing,
        'link_detailed': obj.show_detailed,
        'link_fulltext': obj.show_fulltext,
        'link_publisher': obj.show_viewpublisher,
        'groupsby_all': obj.groupsby_type,
        'groupsby_year': obj.groupsby_year,
        'groupsby_doc': obj.groupsby_doc,
        'adv_article_volume': obj.show_article_volume,
        'adv_article_volume_number': obj.show_article_volume_number,
        'adv_article_volume_pages': obj.show_article_volume_pages,
        'adv_thesis_directors': obj.show_thesis_directors,
        'adv_thesis_pages': obj.show_thesis_pages,
        'adv_report_working_papers_pages': obj.show_report_working_papers_pages,
        'adv_conf_proceed_place': obj.show_conf_proceed_place,
        'adv_conf_proceed_date': obj.show_conf_proceed_date,
        'adv_conf_paper_journal_name': obj.show_conf_paper_journal_name,
        'adv_book_isbn': obj.show_book_isbn,
        'adv_book_doi': obj.show_book_doi,
        'adv_book_chapter_isbn': obj.show_book_chapter_isbn,
        'adv_book_chapter_doi': obj.show_book_chapter_doi,
        'adv_patent_status': obj.show_patent_status
    }


def get_options_from_params(params):
    return {
        'is_extern': False,
        'url': params['url'],
        'format': params['format'],
        'bullet': params['bullet'],
        'thumb': params['thumb'] == 'true',
        'summary': params['summary'] == 'true',
        'link_authors': params['link_authors'] == 'true',
        'link_print': params['link_print'] == 'true',
        'link_detailed': params['link_detailed'] == 'true',
        'link_fulltext': params['link_fulltext'] == 'true',
        'link_publisher': params['link_publisher'] == 'true',
        'groupsby_all': params['groupsby_all'],
        'groupsby_year': params['groupsby_year'],
        'groupsby_doc': params['groupsby_doc'],
        'pending_publications': params['pending_publications'] == 'true',
        'adv_article_volume': params['adv_article_volume'] == 'true',
        'adv_article_volume_number': params['adv_article_volume_number'] == 'true',
        'adv_article_volume_pages': params['adv_article_volume_pages'] == 'true',
        'adv_thesis_directors': params['adv_thesis_directors'] == 'true',
        'adv_thesis_pages': params['adv_thesis_pages'] == 'true',
        'adv_report_working_papers_pages': params['adv_report_working_papers_pages'] == 'true',
        'adv_conf_proceed_place': params['adv_conf_proceed_place'] == 'true',
        'adv_conf_proceed_date': params['adv_conf_proceed_date'] == 'true',
        'adv_conf_paper_journal_name': params['adv_conf_paper_journal_name'] == 'true',
        'adv_book_isbn': params['adv_book_isbn'] == 'true',
        'adv_book_doi': params['adv_book_doi'] == 'true',
        'adv_book_chapter_isbn': params['adv_book_chapter_isbn'] == 'true',
        'adv_book_chapter_doi': params['adv_book_chapter_doi'] == 'true',
        'adv_patent_status': params['adv_patent_status'] == 'true'
    }
