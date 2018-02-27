jQuery(function($) {

	$('#btn-preview').click(function () {
		var params = {};
        params['url'] = $("#id_url").val();
		params['bullet'] = $("#id_bullets_type").find(":selected").val();
		params['thumb'] = $("#id_show_thumbnail").is(':checked');
		params['groupsby_all'] = $("#id_groupsby_type").find(":selected").val();
		params['groupsby_year'] = $("#id_groupsby_year").find(":selected").val();
		params['groupsby_doc'] = $("#id_groupsby_doc").find(":selected").val();
		params['link_title'] = $("#id_show_linkable_titles").is(':checked');
		params['link_authors'] = $("#id_show_linkable_authors").is(':checked');
		params['link_print'] = $("#id_show_links_for_printing").is(':checked');
		params['link_detailed'] = $("#id_show_detailed").is(':checked');
		params['link_fulltext'] = $("#id_show_fulltext").is(':checked');
		params['link_publisher'] = $("#id_show_viewpublisher").is(':checked');
        $.get('/preview/', {params: params}, function (data) {
            ($("#display-mrc21xml").html(data));
        });
    });

	$('.fa-clipboard').click(function () {
		var $temp = $('<input>');
		$('body').append($temp);
		$temp.val($(this).parent().siblings('input').val()).select();
		document.execCommand("copy");
		$temp.remove();
    });


	$(document).ready(function() {
		var selected = $('#id_groupsby_type').find(':selected').val();
		if (selected.indexOf('YEAR') != -1){
			$('#id_groupsby_year').hide();
		} else {
			$('#id_groupsby_doc').hide();
		}
	});

    $('#id_groupsby_type').change(function () {
		var selected = $('#id_groupsby_type').find(':selected').val();
		if (selected.indexOf('YEAR') != -1){
			$('#id_groupsby_year option:eq(0)').prop('selected', true);
			$('#id_groupsby_year').hide();
			$('#id_groupsby_doc').show();
			$('#id_groupsby_doc option:eq(0)').prop('selected', true);
		} else {
			$('#id_groupsby_doc option:eq(0)').prop('selected', true);
			$('#id_groupsby_doc').hide();
			$('#id_groupsby_year').show();
			$('#id_groupsby_year option:eq(0)').prop('selected', true);
		}
    });

});
