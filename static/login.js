
// login feedback
$('#login-form').on('submit', function(e) {
    e.preventDefault();

    console.log("I'm here!");
    if (e=="You are logged in!") {
        bootbox.alert("You are logged in!");
    } else {
        bootbox.alert("Verify email and password entered is correct.");
    }
});

