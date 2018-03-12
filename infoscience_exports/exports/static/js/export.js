jQuery(function($) {

    function change_lang(ln) {
        $('#selected_lang').val(ln);
        $('#change_lang_form').submit();
        return true;
    }

    $('.change_lang_en').click(
        function() {
            return change_lang('en');
        });

    $('.change_lang_fr').click(
        function() {
            return change_lang('fr');
        });

	$('#btn-submit').click(function () {
		$('#id_groupsby_year').prop('disabled', false);
		$('#id_groupsby_doc').prop('disabled', false);
		$('#export_form').submit();
    });

	$('#btn-preview').click(function () {
		$("#display-mrc21xml").html('<span>'+$("#display-mrc21xml").attr('data-progress')+'</span>');
		var params = {};
        params['url'] = $("#id_url").val();
		/*params['format'] = $("#id_formats_type").find(":selected").val();*/
		params['bullet'] = $("#id_bullets_type").find(":selected").val();
		params['thumb'] = $("#id_show_thumbnail").is(':checked');
		params['groupsby_all'] = $("#id_groupsby_type").find(":selected").val();
		params['groupsby_year'] = $("#id_groupsby_year").find(":selected").val();
		params['groupsby_doc'] = $("#id_groupsby_doc").find(":selected").val();
		params['pending_publications'] = $("#id_show_pending_publications").is(':checked');
		params['link_title'] = $("#id_show_linkable_titles").is(':checked');
		params['link_authors'] = $("#id_show_linkable_authors").is(':checked');
		params['link_print'] = $("#id_show_links_for_printing").is(':checked');
		params['link_detailed'] = $("#id_show_detailed").is(':checked');
		params['link_fulltext'] = $("#id_show_fulltext").is(':checked');
		params['link_publisher'] = $("#id_show_viewpublisher").is(':checked');
        $.get(INFOSCIENCE_PATH+'/preview/', {params: params}, function (data) {
            ($("#display-mrc21xml").html(data));
        });
    });

	$('.fa-clipboard').click(function () {
		var copyText = INFOSCIENCE_DOMAIN+$(this).parent().siblings('input').val();
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
		if (selected.indexOf('YEAR') != -1){
			$('#id_groupsby_year').hide();
		} else if (selected.indexOf('DOC') != -1) {
			$('#id_groupsby_doc').hide();
		} else {
			$('#id_groupsby_year').prop('disabled', true);
 			$('#groupby2-label').css("color", 'grey');
			$('#id_groupsby_doc').hide();
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
