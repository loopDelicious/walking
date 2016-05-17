

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
        '<form action="/add_destination" method="POST" class="popUpAdd"><input type="hidden" name="landmark_id"' + 
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
      var coordinates = response.coordinates;
      var place_name = response.place_name;
      L.marker([coordinates[1], coordinates[0]]).addTo(map);
      // var routeLayer = L.mapbox.featureLayer(response, {
      //   pointToLayer: function(place_name, coordinates) {
      //     return L.circleMarker(coordinates, {
      //       fillColor: '#ff0000',
      //       fillOpacity: 0.8,
      //       stroke: false
      //     });
      //   }
      // }).addTo(map);
    },
  });
});


// Add destination to session 
// use $.on() vs. $('selector').on to add asynchronous event listener
// that will watch for newly added DOM elements
$(document).on('submit', '.popUpAdd', function(e) {
  e.preventDefault();
  $.ajax({
    type:  "POST",
    url: '/add_destination',
    data: {
      'landmark_id': this.dataset.id
    }, 
    success: function() {
      // FIXME turn marker blue
      // FIXME close popup
    },
  });
});


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

// establish route polyline
var polyline = L.polyline([]).addTo(map);

// get route directions from Mapbox Directions API via ajax call
$('#get-directions').on('click', function(e) {
  $.ajax({
    type: "GET",
    url: '/route_directions',
    success: function(response) {
      var route = response.routes[0].geometry.coordinates;
      route = route.map(function(point) {
        return [point[1], point[0]];
      });
      polyline.setLatLngs(route);
      var coordinates = response.waypoints.forEach(function(waypoint) {
        L.marker([waypoint.location[1],waypoint.location[0]]).addTo(map);
      });
      // map.setView(polyline.getLatLng(), 14);
      // find some other way to pan to route
      // FIXME do I need to add my markers to a route session variable - to clear the markers from the UI?
    }
  });
});


// FIXME NEED to direct success function to select origin again
// clear route from map by removing waypoints in session
$('#clear').on('click', function(e) {
  e.preventDefault();
  $.post('/clear', function() {
    if (marker != null) {
      map.removeLayer(marker);
    };
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






// jQuery.fn.extend({
//   flash: function(message) {
//     $('#jquery-flash-container').text(message).show();
//     setTimeout(function(){
//       $('#jquery-flash-container').fadeOut();
//     }, 5000);
//   }
// });

// $(document).flash('hello world');

