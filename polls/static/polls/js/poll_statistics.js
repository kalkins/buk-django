function update() {
    var index = $('input[name=option]:checked').parent().index();

    $('.statistics')
        .removeClass('visible')
        .eq(index)
            .addClass('visible');
}

$(document).ready(function() {
    // Run at start, as the browser will remember
    // which was checked when reloading the page
    update();

    $('input[name=option]').change(function() {
        update();
    });
});
