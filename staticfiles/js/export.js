jQuery(function($) {

	$('#btn-preview').click(function () {
        var url = $("#id_url").val();
        $.get('/preview/', {url: url}, function (data) {
            ($("#display-mrc21xml").html(data));
        });
    });

});
