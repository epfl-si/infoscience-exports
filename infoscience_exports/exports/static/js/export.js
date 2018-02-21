jQuery(function($) {

	$('#btn-preview').click(function () {
		var params = {};
        params['url'] = $("#id_url").val();
		params['bullet'] = $("#id_bullets_type").find(":selected").text();
		params['thumb'] = $("#id_show_thumbnail").is(':checked');
        $.get('/preview/', {params: params}, function (data) {
            ($("#display-mrc21xml").html(data));
        });
    });

});
