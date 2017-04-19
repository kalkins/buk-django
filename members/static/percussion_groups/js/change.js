$(document).ready(function() {
    $('.save-button').click(function() {
        var leader = $('input[name=group-leader]:checked').data('id');
        var members = [];
        $('.col-member-select input[type=checkbox]:checked').each(function() {
            members.push($(this).data('id'));
        });

        $.post({
            url: '',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            data: {
                leader: leader,
                members: members,
            },
            success: function(data) {
                if (typeof data['success'] == 'undefined' || !data['success']) {
                    error = true;
                    if (typeof data['error'] == 'undefined') {
                        alert('Det har oppstått en feil. Ta kontakt med webkom.');
                    } else {
                        alert(data['error']);
                    }
                } else {
                    document.location.href = data['next'];
                }
            }
        });
    });
});
