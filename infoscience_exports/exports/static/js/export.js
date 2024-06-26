jQuery(function($) {

    function change_lang(ln) {
        $('#selected_lang').val(ln);
        $('#change_lang_form').submit();
        return true;
    }

    $('.change_lang_en').click(function() {
        return change_lang('en');
    });

    $('.change_lang_fr').click(function() {
        return change_lang('fr');
    });

	$('#btn-submit').click(function () {
		$('#id_groupsby_year').prop('disabled', false);
		$('#id_groupsby_doc').prop('disabled', false);
		$('#export_form').submit();
    });

	$('#display-mrc21xml').ready(function () {
		$('#display-mrc21xml-loading').hide();
		$("#display-mrc21xml").show();
	});

	$('#display-mrc21xml').load(function () {
		$('#display-mrc21xml-loading').hide();
		$("#display-mrc21xml").show();
	});

	$('#btn-preview').click(function () {
		$('#display-mrc21xml-loading').show();
		$("#display-mrc21xml").hide();
		var params = {};
        params['url'] = $("#id_url").val();
		params['format'] = $("#id_formats_type").find(":selected").val();
		params['bullet'] = $("#id_bullets_type").find(":selected").val();
		params['thumb'] = $("#id_show_thumbnail").is(':checked');
		params['summary'] = $("#id_show_summary").is(':checked');
		params['groupsby_all'] = $("#id_groupsby_type").find(":selected").val();
		params['groupsby_year'] = $("#id_groupsby_year").find(":selected").val();
		params['groupsby_doc'] = $("#id_groupsby_doc").find(":selected").val();
		params['pending_publications'] = $("#id_show_pending_publications").is(':checked');
		params['link_authors'] = $("#id_show_linkable_authors").is(':checked');
		params['link_print'] = $("#id_show_links_for_printing").is(':checked');
		params['link_detailed'] = $("#id_show_detailed").is(':checked');
		params['link_fulltext'] = $("#id_show_fulltext").is(':checked');
		params['link_publisher'] = $("#id_show_viewpublisher").is(':checked');
		params['adv_article_volume'] = $("#id_show_article_volume").is(':checked');
		params['adv_article_volume_number'] = $("#id_show_article_volume_number").is(':checked');
		params['adv_article_volume_pages'] = $("#id_show_article_volume_pages").is(':checked');
		params['adv_thesis_directors'] = $("#id_show_thesis_directors").is(':checked');
		params['adv_thesis_pages'] = $("#id_show_thesis_pages").is(':checked');
		params['adv_report_working_papers_pages'] = $("#id_show_report_working_papers_pages").is(':checked');
		params['adv_conf_proceed_place'] = $("#id_show_conf_proceed_place").is(':checked');
		params['adv_conf_proceed_date'] = $("#id_show_conf_proceed_date").is(':checked');
		params['adv_conf_paper_journal_name'] = $("#id_show_conf_paper_journal_name").is(':checked');
		params['adv_book_isbn'] = $("#id_show_book_isbn").is(':checked');
		params['adv_book_doi'] = $("#id_show_book_doi").is(':checked');
		params['adv_book_chapter_isbn'] = $("#id_show_book_chapter_isbn").is(':checked');
		params['adv_book_chapter_doi'] = $("#id_show_book_chapter_doi").is(':checked');
		params['adv_patent_status'] = $("#id_show_patent_status").is(':checked');

		full_url = INFOSCIENCE_PATH + '/preview/?' + $.param(params);
		$("#display-mrc21xml").attr("src", full_url);
    });

	$('.fa-clipboard').click(function () {
		var copyText = $(this).parent().siblings('input').val();
		var $temp = $('<input>');
		$('body').append($temp);
		$temp.val(copyText).select();
		document.execCommand("copy");		
		$temp.remove();
		$(this).parent().tooltip('hide');
        $(this).parent().attr('data-original-title', copyText);
        $(this).parent().tooltip('fixTitle');
        $(this).parent().tooltip('show');
    });

	$('.fa-clipboard').mouseout(function () {
	  	$(this).parent().tooltip('hide');
        $(this).parent().attr('data-original-title', $(this).parent().attr('data-tip'));
        $(this).parent().tooltip('fixTitle');
        $(this).parent().tooltip('show');
	});

	$(document).ready(function() {
		$('[data-toggle="tooltip"]').tooltip();

		var selected = $('#id_groupsby_type').find(':selected').val();
    if (selected !== undefined) {
      if (selected.indexOf('YEAR') != -1) {
        $('#id_groupsby_year').hide();
      } else if (selected.indexOf('DOC') != -1) {
        $('#id_groupsby_doc').hide();
      } else {
        $('#id_groupsby_year').prop('disabled', true);
        $('#groupby2-label').css("color", 'grey');
        $('#id_groupsby_doc').hide();
      }
    }
	});

    $('#id_groupsby_type').change(function () {
		var selected = $('#id_groupsby_type').find(':selected').val();
		if (selected.indexOf('YEAR') != -1){
			$('#id_groupsby_year option:eq(0)').prop('selected', true);
			$('#id_groupsby_year').hide();
			$('#id_groupsby_doc').show();
			$('#id_groupsby_doc').prop('disabled', false);
 			$('#groupby2-label').css("color", 'black');
			$('#id_groupsby_doc option:eq(0)').prop('selected', true);
		} else  if (selected.indexOf('DOC') != -1) {
			$('#id_groupsby_doc option:eq(0)').prop('selected', true);
			$('#id_groupsby_doc').hide();
			$('#id_groupsby_year').show();
			$('#id_groupsby_year').prop('disabled', false);
 			$('#groupby2-label').css("color", 'black');
			$('#id_groupsby_year option:eq(0)').prop('selected', true);
		} else {
			$('#id_groupsby_year option:eq(0)').prop('selected', true);
			$('#id_groupsby_year').show();
			$('#id_groupsby_year').prop('disabled', true);
 			$('#groupby2-label').css("color", 'grey');
			$('#id_groupsby_doc').hide();
		}
    });

});
