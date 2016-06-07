
//registration feedback
$('.btn-primary').on('submit', function(response) {
    response.preventDefault();
    if (response=="An account has already been created for this email.") {
        bootbox.alert("An account has already been created for this email.");
    } else {
        bootbox.alert("Your account has been created.");
    }
});