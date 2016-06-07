// logout feedback
$('.btn-logout').on('submit', function(response) {
    response.preventDefault();
    if (response=="Logged out.") {
        bootbox.alert("Logged out.");
    }
});
