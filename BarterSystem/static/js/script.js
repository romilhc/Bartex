/**
 * Created by Romil Chauhan on 4/6/2017.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});




function signin() {
    alert("setup works");
    var email = $('#email').val();
    var password = $('#password').val();
    var signinData = {'email': email, 'password': password};

    alert(email);
    alert(password);
    event.preventDefault();
    $.ajax({
        method: "POST",
        url: "/home/",
        data: signinData,
        dataType: 'json',
        "beforeSend": function(xhr, settings) {
            console.log("Before Send");
            $.ajaxSettings.beforeSend(xhr, settings);
            alert("Sending");
        },
        success: function(result){
            status = result.status;
            session_id = result.session_id;
            if(status=="success") {
                alert("Success");
                alert(status);
            }
            else {
                alert(status);
                location.reload();
            }

        }
    });

}