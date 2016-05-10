
  var map;
  // create a new Google Maps object
  function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: -34.397, lng: 150.644},
      zoom: 8
    });
  }



<div id="yourinfo"></div>
    
    <script type="text/javascript" src="http://www.google.com/jsapi?key=<YOUR_GOOGLE_API_KEY>"></script>
    
    <script type="text/javascript">
        if(google.loader.ClientLocation) {
            visitor_lat = google.loader.ClientLocation.latitude;
            visitor_lon = google.loader.ClientLocation.longitude;
            visitor_city = google.loader.ClientLocation.address.city;
            visitor_region = google.loader.ClientLocation.address.region;
            visitor_country = google.loader.ClientLocation.address.country;
            visitor_countrycode = google.loader.ClientLocation.address.country_code;
            document.getElementById('yourinfo').innerHTML = '<p>Lat/Lon: ' + visitor_lat + ' / ' + visitor_lon + '</p><p>Location: ' + visitor_city + ', ' + visitor_region + ', ' + visitor_country + ' (' + visitor_countrycode + ')</p>';
        } else {
            document.getElementById('yourinfo').innerHTML = '<p>Whoops!</p>';
        }
    </script>


    // <!-- call the initMap function after the API has loaded -->
    <script src="https://maps.googleapis.com/maps/api/js?callback=initMap&libraries=places"
        async defer>
    </script>

var input = document.getElementById('pac-input');

// Get the HTML input element for the auto-complete search box
map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

// Create the autocomplete object
var autocomplete = new google.maps.places.Autocomplete(input, options);


google.maps.event.addDomListener(window, 'load', initialize);