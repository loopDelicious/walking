

// default mapbox public access token
L.mapbox.accessToken = 'pk.eyJ1Ijoiam95Y2VsaW43OSIsImEiOiJjaW8zNzk5bHcwMDA5dzFrcXd6anpnY2xoIn0.ovObS9ODfNsnaa8ie--fKQ';

// load base map of San Francisco
var map = L.mapbox.map('map', 'mapbox.streets', {
    accessToken: L.mapbox.accessToken,
    zoomControl: false,
    zoom: 12,  // starting zoom
    minZoom: 9, // farthest you can zoom out
    maxZoom: 16,  // closest you can zoom in
    center: [37.7749, -122.4194],  // starting position to center map on SF
    interactive: true // make interactive instead of static
    });
 
// add search box to map
var geocoderControl = L.mapbox.geocoderControl('mapbox.places',{
  autocomplete: true,
  keepOpen: true
});
geocoderControl.addTo(map);

// place a marker for entered address
geocoderControl.on('select', function(e) {
  var coordinates = e.feature.geometry.coordinates;
  L.marker([coordinates[1], coordinates[0]]).addTo(map);


  // var popupContent = 

});

// var popupContent = 
//         '<h2>' + feature.properties.name + '</h2>' + 
//         feature.properties.description + 
//         '<form action="/add_waypoint"><input type="hidden" name="landmark_id"' + 
//         feature.id + '"><button id="popupButton" class="popUp"' + 
//         feature.id + feature.properties.name + '">Add destination</button></form>'; 

// popUp and ask user to confirm starting point for trip, if so,
// add to session['waypoints'], add to route, and prompt user for another waypoint

// load the initial landmark set into a featureLayer from geojson for display
var initialLandmarkLayer = L.mapbox.featureLayer().addTo(map);
initialLandmarkLayer.loadURL('/initial_landmarks.geojson');

// load the landmark markers into a featureLayer from geojson, but don't add to map
var landmarkLayer = L.mapbox.featureLayer();
landmarkLayer.loadURL('/landmarks.geojson');

// clicking on a landmark will center the map and display nearby landmarks
initialLandmarkLayer.on('click', function(e) {
    map.setView(e.latlng, 14);
    map.panTo(e.latlng);
    landmarkLayer.addTo(map);
    map.removeLayer(initialLandmarkLayer);
  });


//  FIXME how do I remove the initial landmark layer so that doesn't load?
//  map.removeLayer(initialLandmarkLayer);

// create popups for landmarks
landmarkLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = marker.feature;    

    var popupContent = 
        '<h2>' + feature.properties.name + '</h2>' + 
        feature.properties.description + 
        '<form action="/add_waypoint"><input type="hidden" name="landmark_id"' + 
        feature.id + '"><button id="popupButton" class="popUp"' + 
        feature.id + feature.properties.name + '">Add destination</button></form>'; 

    // Create custom popup content
    // var popupContent = '<h2>' + feature.properties.name + '</h2>' + feature.properties.description;
                        
    // var popoverContent = 
    //     '<form action="/add_waypoint"><input type="hidden" name="landmark_id"><button id="popupButton" data-toggle="popover" data-placement="bottom" data-trigger="focus" class="trigger" ' + feature.id + feature.properties.name + '">Add waypoint</button></form>'; 

    marker.bindPopup(popupContent, {
        closeButton: false,
        minWidth: 120
    });

});

// ADJUST SENSITIVITY SO CAN CLICK
// display popups on mouseover
landmarkLayer.on('mouseover', function(e) {
    e.layer.openPopup();
    });

// $('#popup').ready(function(){
//     $('[data-toggle="popover"]').popover(); 
// });

// $(document).ready(function(){
//     $('[data-toggle="popover"]').popover();   
// });
// FIXME popover doesn't work

// FIXME START HERE
// open popover content on clicking popup
// $('#trigger').on('click', '.trigger', function(e) {
//     alert('Hello from Toronto!');
// });

// FIXME when do i wrap in a function vs. calling ajax directly?  repeatable?


// create a directions object, from which the layer and inputs will pull data
var directions = L.mapbox.directions({
  profile: 'mapbox.walking'
});

var directionsLayer = L.mapbox.directions.layer(directions)
    .addTo(map);

var directionsInputControl = L.mapbox.directions.inputControl('inputs', directions)
    .addTo(map);

var directionsErrorsControl = L.mapbox.directions.errorsControl('errors', directions)
    .addTo(map);

var directionsRoutesControl = L.mapbox.directions.routesControl('routes', directions)
    .addTo(map);

var directionsInstructionsControl = L.mapbox.directions.instructionsControl('instructions', directions)
    .addTo(map);



// If no waypoints in session, prompt user to add origin, also add waypoints popups
// should show get started and add origin

// Geocode user-entered address to lat_lng coordinates, and add to session
$('#address-input').on('submit', function(e) {
  e.preventDefault();
  $.ajax({
    type: "POST",
    url: '/geocode',
    data: {
      'destination': $('#user-input').val()
    },
    success: function(response) {
      alert('Destination added.' + response.coordinates + response.place_name);
      var coordinates = response.feature.geometry.coordinates;
      L.marker([coordinates[1], coordinates[0]]).addTo(map);
      map.setView(layer.getLatLng(), 14);
      layer.openPopup();
    },
    // dataType: dataType
  });
});


// Add destination to session 
$('#add_destination').on('click', function(e) {
  e.preventDefault();
  $.get('/add_destination', {'landmark_id': this.dataset.id}, function(){
    add_destination();
  });
  $.ajax({
    type: "POST",
    url: '/add_destination',
    data: {
      'destination': this.dataset.id
      // FIXME here.
    }
  })
});

// establish route layer
// var routeLayer = L.mapbox.featureLayer();

// get directions for all destinations in the session
// $('#get-directions').on('click', function(e) {
//   e.preventDefault();
//   routeLayer.addTo(map).loadURL('/route_directions');
// }); 

// establish route polyline
var polyline = L.polyline([]).addTo(map);

// map.on('click', function(e) {
//         // Let's add a callback to makeMarker so that it can draw the route only
//         // *after* it's done processing the marker adding.
//         makeMarker(e, drawRoute);
//     });

// function makeMarker(e, done) {
//     var marker = L.marker(e.latlng, { draggable: true }).addTo(map);
//     marker.on('dragend', drawRoute);
//     waypoints.push(marker);
//     return done();
// }

$('#get-directions').on('click', function(e) {
  e.preventDefault();
  $.ajax({
    type: "GET",
    url: '/route_directions',
    success: function(response) {
      console.log(response);
      var route = response['route']['legs'];
      console.log(route);
      // polyline.setLatLngs(route);
    },
  });
});


// $.get(directionsUrl, function(data) {
//     var route = data.routes[0].geometry.coordinates;
//     route = route.map(function(point) {
//         // Turns out if we zoom out we see that the lat/lngs are flipped,
//         // which is why it didn't look like they were being added to the
//         // map. We can invert them here before drawing.
//         return [point[1], point[0]];
//     });
//     polyline.setLatLngs(route);
// });



// FIXME NEED to direct success function to select origin again
// clear route from map by removing waypoints in session
$('#clear').on('click', function(e) {
  e.preventDefault();
  $.post('/clear', function() {
    if (routeLayer != null) {
      map.removeLayer(routeLayer);
    }
    alert('Cleared!');
  });
});

// // Initial view and interaction:
// // prompt user to input origin
// // establish landmark markers but don't add to map yet
// // load first 10 landmarks within 1 mile of current user
// // allow user to explore nearby landmarks with pop-ups in the map
// // allow user to search for next destination
// // toggle layers to display landmarks by type
// // update landmarks displayed with ajax calls
// // CTA is to add new waypoint

// // creating the walk:
// // create the initial directions object, from which the layer
// // and inputs will pull data.
// // once a waypoint has been added, determine route, time and directions to waypoint
// // prompt the user to add another waypoint OR save the walk to their profile

// // User can delete walks from their display
// // User can rate landmarks, add new ones, leave public comments



