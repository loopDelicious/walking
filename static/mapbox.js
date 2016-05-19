// ================================================================================
//  Initializing the map and controls
// ================================================================================

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
});

// popUp and ask user to confirm starting point for trip, if so,
// add to session['waypoints'], add to route, and prompt user for another waypoint

// ================================================================================
//  Initializing the landmark layer and popups
// ================================================================================

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
    // $.ajax({
    //   type: "GET",
    //   url: "/prompt_origin",
    //   success: function(response) {
    //     alert(response);
    //   }
    // });

    var marker = e.layer,
        feature = marker.feature;

    // stylize markers
    // marker.setIcon(L.mapbox.marker.icon({
    // 'marker-symbol': 'star',
    // 'marker-color': '#D3D3D3',
    // 'marker-size': 'small',
    // 'riseOnHover': 'true',
    // }));  

    var popupContent = 
        '<h2>' + feature.properties.name + '</h2>' + feature.properties.description + 
        '<form action="/add_destination" method="POST" class="popUpAdd"><input type="hidden" id="popup-id" name="landmark_id" value="' + 
        feature.id + '"><button id="popupButton" class="popUp" data-id="' + 
        feature.id + '" data-name="' + feature.properties.name + '">Add destination</button></form>'; 

                        
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

// ================================================================================
//  User interactions to construct a trip route
// ================================================================================

$.ajax({
  type: "GET",
  url: '/has_origin',
  success: function(response) {
    if (response.status == false) {
      alert("Where would you like to begin?");
    }
  }
});

function add_destination(response) {
  var coordinates = response.coordinates;
  var place_name = response.place_name;
  L.marker([coordinates[1], coordinates[0]], {
    'title': place_name,
    'riseOnHover': true
  }).addTo(routeLayer);
};

// Geocode user-entered address to lat_lng coordinates, and add to session
$('#address-input').on('submit', function(e) {
  e.preventDefault();
  $.ajax({
    type: "POST",
    url: '/geocode',
    data: {
      'destination': $('#user-input').val()
    },
    success: add_destination,
  });
  $("#address-input").trigger('reset');
  alert('Destination added.');
});

// dan: draw route everytime new waypoint is added

// Add destination to session 
// use $.on() vs. $('selector').on to add asynchronous event listener
// that will watch for newly added DOM elements
$(document).on('submit', '.popUpAdd', function(e) {
  e.preventDefault();
  $.ajax({
    type:  "POST",
    url: '/add_destination',
    data: {
      'destination': $('#popup-id').val()
    }, 
    success: add_destination,
  });
  $('.popup').trigger('reset');
      // FIXME turn marker blue
      // FIXME close popup
});


// establish layer of selected (new) markers for the trip
var routeLayer = L.mapbox.featureLayer().addTo(map);

// create popups for selected (new) landmarks
routeLayer.on('layeradd', function(e) {
    var marker = e.layer;
  
    // console.log(marker);  FIXME add feature NAME
    var popupContent = 
        '<h2>' + marker.options.title + '</h2>' +
        '<p>Destination added</p>'; 

    marker.bindPopup(popupContent, {
        closeButton: false,
        minWidth: 120
    });
});

routeLayer.on('mouseover', function(e) {
    e.layer.openPopup();
    });


// ================================================================================
//  Finalizing a trip and getting route directions
// ================================================================================

// add layer with landmark markers to map

function return_all_waypoints() {
  $.ajax({
    type: "GET",
    url: '/return_all_waypoints',
    success: function(response) {
      for (var i = 0; i < response.length; i++) {
        var coordinates = response.coordinates;
        var place_name = response.place_name;
        L.marker([coordinates[1], coordinates[0]]).addTo(routeLayer);
      };
    }
  });
};

// establish polyline with path of landmarks
var polyline = L.polyline([]).addTo(map);


// get route directions from Mapbox Directions API via ajax call
$('#get-directions').on('click', function(e) {
  $.ajax({
    type: "GET",
    url: '/origin_and_destination',
    success: function(data) {
      var origin = data.origin.place_name.split(',')[0];
      var destination = data.destination.place_name.split(',')[0];
      $('#routes').append('<p>'+ origin + ' to ' + destination +': </p>');
    }
  });
  $.ajax({
    type: "GET",
    url: '/route_directions',
    success: function(response) {
      var route = response.routes[0].geometry.coordinates;
      route = route.map(function(point) {
        return [point[1], point[0]];
      });
      polyline.setLatLngs(route);
      // var coordinates = response.waypoints.forEach(function(waypoint) {
      //   L.marker([waypoint.location[1],waypoint.location[0]]).addTo(polyline);
      // });
      var steps = response.routes[0].legs[0].steps.forEach(function(step) {
        $('#instructions').append('<p>'+ step.maneuver.instruction + ' for ' + step.distance + ' meters</p>');
      });
    }
    // FIXME convert meters to miles
    // map.setView(polyline.getLatLng(), 14);
    // map.setView(polyline.latlng, 14);
  });
});


// FIXME NEED to direct success function to select origin again
// clear route from map by removing waypoints in session
$('#clear').on('click', function(e) {
  e.preventDefault();
  $.post('/clear', function() {
    map.removeLayer(routeLayer);
    // if (routeLayer instanceof L.mapbox.featureLayer) {
    //   console.log('hi');
    //   map.removeLayer(routeLayer);
    // };
    if (polyline instanceof L.Polyline) {
      map.removeLayer(polyline);
    }
    polyline = L.polyline([]).addTo(map);
    routeLayer = L.mapbox.featureLayer().addTo(map);
    location.reload();
    alert('Cleared!');
  });
});


// debugger function to display python session variable
// python returns a jsonified string, jquery interprets as object so must re-stringify
// use optional 3rd parameter to indicate 4 spaces JS indentation
// <pre> tags indicate to maintain pre-formatted response
$('#debugger').on('click', function(e){
  $.ajax({
    type: "GET",
    url: '/debugger',
    success:  function(response) {
      response = JSON.stringify(response, null, 4);
      $.colorbox({
        html: "<pre>" + response + "</pre>",
        width: '500px',
        height: '500px'
      });    
    }
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

