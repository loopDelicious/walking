// MVP:
// landmark layer: load subset of all landmarks initially
// popups: allow user to explore nearby landmarks with pop-ups in the map
// geocode: allow user to text-search for next destination
// directions: determine route and directions to waypoint

// PHASE 2 ideas:
// UI / UX enhancements
// filter: toggle layers to display landmarks by type (park, art, stairwells)
// save the walk to user profile (and delete)
// user can rate landmarks, add new ones, upload photos, leave public comments

// ================================================================================
//  Initializing the map and controls
// ================================================================================

// default mapbox.js API public access token
L.mapbox.accessToken = 'pk.eyJ1Ijoiam95Y2VsaW43OSIsImEiOiJjaW8zNzk5bHcwMDA5dzFrcXd6anpnY2xoIn0.ovObS9ODfNsnaa8ie--fKQ';

var latlng = [37.7749, -122.4194]

// load base map of San Francisco
var map = L.mapbox.map('map', 'mapbox.streets', {
    accessToken: L.mapbox.accessToken,
    zoomControl: false,
    attributionControl: false,
    zoom: 12,  // starting zoom
    minZoom: 9, // farthest you can zoom out
    maxZoom: 16,  // closest you can zoom in
    center: latlng,  // starting position to center map on SF
    interactive: true, // make interactive instead of static
    });

// add search box geocoder to map
var geocoderControl = L.mapbox.geocoderControl('mapbox.places',{
  autocomplete: true,
  keepOpen: true,
  position: 'topleft',
  // rippleEffect: true,
}).addTo(map);

// https://www.mapbox.com/mapbox.js/api/v2.4.0/l-mapbox-geocoder/
// where do I pass through optional parameters proximity=latlng to bias search results?
// can't bias autocomplete results by SF proximity since /geocoding is occuring on backend and included in query parameters

// display variable copy in the geocoder depending if the user has entered an origin
// http://stackoverflow.com/questions/28551603/change-the-placeholder-text-of-an-input-field-after-initializing
map.addEventListener('ready', function () {
  $.ajax({
    type: "GET",
    url: '/has_origin',
    success: function(response) {
      if (response.status == false) {
        document.querySelector('.leaflet-control-mapbox-geocoder-form input').placeholder = "Where do you want to go?";
      } else {
        document.querySelector('.leaflet-control-mapbox-geocoder-form input').placeholder = "Where to next?";
      }
    }
  });
});

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
new L.Control.Zoom({ position: 'topleft' }).addTo(map);


// ================================================================================
//  User enters address using geocoder control
// ================================================================================

// place a marker for entered address
geocoderControl.on('select', function(e) {
  var coordinates = e.feature.geometry.coordinates;
  var place_name = e.feature.text;
  // map.panTo(e.latlng);
  confirm_destination(coordinates, place_name);
});

geocoderControl.on('submit', function(e) {
  e.geocoderControl.close();
});

// confirm user selection with dialog to save, add or cancel action
function confirm_destination(coordinates, place_name) {
  bootbox.dialog({
    message: "Add this destination to your trip?",
    title: place_name,
    onEscape: function () {
      $('.bootbox.modal').modal('hide');
    },
    buttons: {
      save: {
        label: "Save to Favorites",
        className: "btn-save",
        callback: function() {
          $.ajax({
            type:  "POST",
            url: '/save_destination',
            data: {
              'coordinates': coordinates, 
              'place_name': place_name,
            }, 
            success: save_destination,
          });
        }      
      },
      cancel: {
        label: "Cancel",
        className: "btn-cancel",
        callback: function() {
          $('.btn-cancel').modal('hide');
        }
      },
      add: {
        label: "Add destination",
        className: "btn-add",
        callback: function() {
          $.ajax({
            type: "POST",
            url: '/add_destination',
            data: {
              'coordinates': coordinates, 
              'place_name': place_name,
            },
            success: add_destination,
          });
        }
      }
    }
  });
};

// ================================================================================
//  Initializing the landmark layer and popups
// ================================================================================

// load the initial landmark set into a featureLayer from geojson for display
var initialLandmarkLayer = L.mapbox.featureLayer().addTo(map);
initialLandmarkLayer.loadURL('/initial_landmarks.geojson');

// load the landmark markers into a featureLayer from geojson, but don't add to map
var landmarkLayer = L.mapbox.featureLayer();
landmarkLayer.loadURL('/landmarks.geojson');

// FIXME when user clicks OR zooms, load the full landmark set (only once)
initialLandmarkLayer.once('click', function(e) {
    map.setView(e.latlng, 14);
    map.panTo(e.latlng);
    landmarkLayer.addTo(map);
    map.removeLayer(initialLandmarkLayer);
  });

// FIXME transition user from initialLandmarkLayer to landmarkLayer and persist
// FIXME how to do zoom / pan on zoom OR click

// create popups for landmarks
landmarkLayer.on('layeradd', function(e) {

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
        '<h2><a href="/landmarks/' + feature.id + '"><img src="' + feature.image + '" />' + feature.properties.name + '</a></h2><p>' + feature.properties.description + '</br>Average Rating: ' + feature.avg_rating + '</p>' + 
        '<form action="/add_destination" method="POST" class="popUpAdd"><input type="hidden" id="popup-id" name="landmark_id" value="' + 
        feature.id + '"><button id="popupButton" class="popUp" data-id="' + 
        feature.id + '" data-name="' + feature.properties.name + 
        '">Add destination</button></form><form action="/save_destination" method="POST" class="popUpSave"><input type="hidden" id="save-id" name="landmark_id" value="' +
        feature.id + '"><button id="saveButton" class="popUpSave" data-id="' +
        feature.id + '" data-name="' + feature.properties.name + '">Save</button></form>'; 

    // if user had added, change to destination added, provide option to remove from trip
    // display average score (if any)
                        
    marker.bindPopup(popupContent, {
        closeButton: false,
        minWidth: 120,
        zoomAnimation: true,
        fadeAnimation: true,
        autoPan: true,
    });
});

// display popups on click, and close popups on mouseout
landmarkLayer.on('click', function(e) {
    e.layer.openPopup();
});
//FIXME adjust sensitivity so user can catch the popup
// landmarkLayer.on('mouseout', function(e) {
//   e.layer.closePopup();
// });


// ================================================================================
//  User interactions to construct a trip route
// ================================================================================

// stand alone function to add destination marker to routelayer
function add_destination(response) {
  var coordinates = response.coordinates;
  var place_name = response.place_name;
  L.marker([coordinates[1], coordinates[0]], {
    'title': place_name,
    'riseOnHover': true
  }).addTo(routeLayer);
  bootbox.alert('Destination added.');
  // closePopup();
};

function save_destination(response) {
  if (response == "Already saved.") {
    bootbox.alert("Destination already saved.");
  } else {
    bootbox.alert("Destination saved.");
  }
};

// Add destination to session via popup
// use $.on() vs. $('selector').on to add asynchronous event listener
// that will watch for newly added DOM elements

// ajax post request to add user-selected pop-up landmark to session
$(document).on('submit', '.popUpAdd', function(e) {
  e.preventDefault();
  $.ajax({
    type:  "POST",
    url: '/add_destination',
    data: {
      'landmark_id': $('#popup-id').val()
    }, 
    success: add_destination,
  });
});

// ajax post request to save user-selected pop-up landmark to db
$(document).on('submit', '.popUpSave', function(e) {
  e.preventDefault();
  $.ajax({
    type:  "POST",
    url: '/save_destination',
    data: {
      'landmark_id': $('#save-id').val()
    }, 
    success: save_destination,
  });
});

// initialize route layer, add to map
var routeLayer = L.mapbox.featureLayer().addTo(map);
var markerList = document.getElementById('marker-list');

// create popups for selected route landmarks
routeLayer.on('layeradd', function(e) {
    var marker = e.layer;
  
    var popupContent = 
        '<h2>' + marker.options.title + '</h2>' +
        '<p>Destination added</p>'; 

    marker.bindPopup(popupContent, {
        closeButton: false,
        minWidth: 120
    });
});

// load the highest rated landmarks into a layer, but don't add to map
// FIXME should the nearest attractions be based on the routeLayer or polyline?
// FIXME /highest_rated.geojson TypeError: cannot convert dictionary update sequence element #0 to a sequence
// var highestRatedLayer = L.mapbox.featureLayer();
// highestRatedLayer.loadURL('/highest_rated.geojson');

// routeLayer.on('ready', function (e) {
//   var highestFeatures = highestRatedLayer.getGeoJSON();

//   // Using Turf, find the nearest highest rated landmarks to the route
//   var nearestHighest = turf.nearest(e.layer.feature, highestFeatures);

//   // Change the nearest hospital to a large marker
//   nearestHighest.properties['marker-size'] = 'large';

//   // Add the new GeoJSON to hospitalLayer
//   highestRatedLayer.setGeoJSON(highestFeatures);
// });

// https://www.mapbox.com/mapbox.js/example/v1.0.0/marker-list-click/
// add destinations to side panel, zoom to marker when clicked
// routeLayer.on('click', function(e) {
//   map.routeLayer.eachLayer(function(layer) {
//     var item = markerList.appendChild(document.createElement('li'));
//     item.innerHTML = layer.toGeoJSON().properties.title;
//     item.onclick = function() {
//       map.setView(layer.getLatLng(), 14);
//       layer.openPopup();
//     };
//   });
// });

// routeLayer.on('layeradd', function(e) {
//   map.routeLayer.eachLayer(function(layer) {
//     var item = markerList.appendChild(document.createElement('li'));
//     item.innerHTML = layer.toGeoJSON().properties.title;
//     item.onclick = function() {
//       map.setView(layer.getLatLng(), 14);
//       layer.openPopup();
//     };
//   });
// });




// ================================================================================
//  Finalizing a trip and getting route directions
// ================================================================================

// add selected landmarks to map route layer
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

// FIXME draw route everytime new waypoint is added

// ajax get request to retrieve route directions from Mapbox Directions API
$('#get-directions').on('click', function(e) {
  var $btn = $(this);
  $btn.text('configuring route...');
  $('#directions').fadeIn();
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
      var duration = response.routes[0].duration;
      var duration_conv = (duration/60).toFixed(0);
      $('#duration').append('<p>'+ duration_conv + ' minutes</p>');

      var steps = response.routes[0].legs[0].steps.forEach(function(step) {
        var meters_conv = step.distance.toFixed(1);
        $('#instructions-list').append('<p><div class="icon heart"></div>'+ step.maneuver.instruction + ' for ' + meters_conv + ' meters</p>');
        // $('#distance-list').append('<p>' + meters_conv + ' meters</p>');
      });
      $btn.text('get route');
    }
    // map.setView(polyline.getLatLng(), 14);
    // map.setView(polyline.latlng, 14);
  });
});

// FIXME: make suggested landmarks bigger when route drawn:  https://www.mapbox.com/help/analysis-with-turf/

// ajax post request to clear route from map by removing waypoints in session
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
    bootbox.alert('Cleared!');
  });
});


// ================================================================================
//  Additional user interaction
// ================================================================================

//do i want to allow users to add a new landmark?
//from geocoder confirm dialog? or separate button?
// ajax post request to add new landmark to database
$('#add-new').on('click', function(e) {
  $.ajax({
    type: "POST",
    url: '/add_new_landmark',
    success: add_destination,
  });
});

// http://leafletjs.com/reference.html#popup
// suggest additional points of interest
// var pointToSegmentDistance(point, segment1, segment 2)


// get step directions and email directions to your phone
// $('#email').on('click', function(e) {
//   e.preventDefault();
//   var email_message = "";
//   $.ajax({
//     type: "POST",
//     url: '/route_directions',
//     success: function(response) {
//       var steps = response.routes[0].legs[0].steps.forEach(function(step) {
//         var meters_conv = step.distance.toFixed(1);
//         email_message += (step.maneuver.instruction + " for " + meters_conv ";\n");
//       });
//     }
//   });
//   $.ajax({
//     type: "POST",
//     url: '/email_directions',
//     data: email_message,
//     success: function() {
//       bootbox.alert('Email has been sent.');
//     },
//   });
// });




// python returns a jsonified string, jquery interprets as object so must re-stringify
// use optional 3rd parameter to indicate 4 spaces JS indentation
// <pre> tags indicate to maintain pre-formatted response

// ajax get request to display python session variable for debugging
$('#debugger').on('click', function(e){
  $.ajax({
    type: "GET",
    url: '/debugger',
    success:  function(response) {
      response = JSON.stringify(response, null, 4);
      bootbox.dialog({
        message: "<pre>" + response + "</pre>",
        title: "Session", 
        buttons: {
          OK: {
            label: "OK",
            className: "btn-OK",
          }
        }
      });
    }   
  });
});

