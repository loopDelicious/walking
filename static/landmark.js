
function rate_landmark() {
  // display rating on landmark details page
}

//ajax post request to save user landmark rating from landmark page to db
// 5 star buttons, each with a value, do i need a form wrapper?
$('.btn.rate').on('click', function(e) {
  $.ajax({})
    type: "POST",
    url: '/rate_landmark',
    data: {
      'landmark_id': $('.btn.rate').val()
    },
    success: rate_landmark,
  });
});
