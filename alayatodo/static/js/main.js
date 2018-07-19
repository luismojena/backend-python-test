$(document).ready(function () {
    $('.information-message').slideDown(500).delay(3000).slideUp(500);

    $('#paginator-selector').on('change', function (e) {
        $('#paginator-selector-form').submit();
    });
});