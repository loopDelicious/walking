

// default mapbox public access token
L.mapbox.accessToken = 'pk.eyJ1Ijoiam95Y2VsaW43OSIsImEiOiJjaW8zNzk5bHcwMDA5dzFrcXd6anpnY2xoIn0.ovObS9ODfNsnaa8ie--fKQ';

// load base map of San Francisco
var map = L.mapbox.map('map', 'mapbox.streets', {
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

// create tooltips for landmarks
landmarkLayer.on('layeradd', function(e) {
    var marker = e.layer,
        feature = marker.feature;    

    var toolTips = 
        '<h2>' + feature.properties.name + '</h2>' + 
        feature.properties.description + '<form action="/add_waypoint"><input type="hidden" name="landmark_id" onclick="openPanel()" value="' + feature.id + '"><button id="popupButton" class="popUp" onclick="openPanel()" data-id="' + feature.id + '" data-name="' + feature.properties.name + '">Add waypoint</button></form>'; 

    marker.bindPopup(toolTips, {
        closeButton: true,
        minWidth: 120
        });
});

// ADJUST SENSITIVITY SO CAN CLICK
// display tooltips on mouseover
landmarkLayer.on('mouseover', function(e) {
    e.layer.openPopup();
});


// If no waypoints in session, prompt user to add origin, also add waypoints popups
// should show get started and add origin
$('.address-input').on('submit', function(e) {
  $.post('/set_origin', function() {
    alert('Origin set')
  });
  e.preventDefault();
});

// HOW DO YOU LEAVE THE USER ON THE PAGE WITH AJAX?
// Add destination to session 
$('.popUp').on('click', function(e) {
  e.preventDefault();
  $.get('/add_waypoint', {'landmark_id': this.dataset.id}, function(){
    add_waypoint();
  });
});

// get directions for all destinations in the session
$('#get-directions').on('click', function(e) {
  e.preventDefault();
  $.get('/route_directions', get_directions_geojson);
});

// FIXME NEED to direct success function to select origin again
// clear route from map by removing waypoints in session
$('#clear').on('click', function(e) {
  e.preventDefault();
  $.post('/clear', function() {
    alert('Cleared!')
  });
});


// Omnivore will AJAX-request this file behind the scenes and parse it:
// omnivore.csv('/mapbox.js/seed_data/sfgov_civic_art.json').addTo(map);


// var map = new mapboxgl.Map({
//     container: 'map', // container id
//     style: 'mapbox://styles/mapbox/streets-v9', //stylesheet location
//     center: lng_lat, // starting position
//     pitch: 0, // pitch in degrees
//     bearing: 0, // bearing in degrees
//     zoom: 11, // starting zoom
//     interactive: true // make interactive instead of static
// });

// L.mapbox.map('map', 'mapbox.streets')
//     .addControl(L.mapbox.geocoderControl('mapbox.places', {
//     .addControl(new mapboxgl.Directions());
//     autocomplete: true,
//     keepOpen: true
//     }));

// // add landmarks layer to map, load geojson, but don't add all to map until origin entered
// var landmarkLayer = L.mapbox.featureLayer().loadURL('/landmarks_geojson');

// // add 15 landmarks to the map

// // when click on any event marker, zoom in and show nearby hiddengems
// eventLayer.on('click', function(e) {
//     map.setView(e.latlng, 14);
//     map.panTo(e.latlng);
//     landmarkLayer.addTo(map);
//     showWithin(e);
//     countWithin(e);
//     showInView();
//     document.getElementById('landmarks').className = "label show";
//   });


// // Center the map and add marker where the user enters origin address 
// // via client-side Google Geocoding API request.
// geocoder = new google.maps.Geocoder();
// geocoder.geocode({ 'address': address }, function(results, status) {
//   if (status == google.maps.GeocoderStatus.OK) {
//     map.setCenter(results[0].geometry.location);
//     var marker = new google.maps.Marker({
//       map: map,
//       position: results[0].geometry.location
//     });
//   }
// });



// // load base map





// // Features on the map:

// // Add zoom and rotation controls to the map.
// map.addControl(new mapboxgl.Navigation());

// // Add driving directions control to the map.


// // FIXME why doesn't this move to the left?
// // move the attribution control out of the way
// map.attributionControl.setPosition('bottomleft');

// // create the initial directions object, from which the layer
// // and inputs will pull data.
// var directions = mapboxgl.directions({
//     profile: 'mapbox.walking'
// });

// var directionsLayer = mapboxgl.directions.layer(directions)
//     .addTo(map);

// var directionsInputControl = mapboxgl.directions.inputControl('inputs', directions)
//     .addTo(map);

// var directionsErrorsControl = mapboxgl.directions.errorsControl('errors', directions)
//     .addTo(map);

// var directionsRoutesControl = mapboxgl.directions.routesControl('routes', directions)
//     .addTo(map);

// var directionsInstructionsControl = mapboxgl.directions.instructionsControl('instructions', directions)
//     .addTo(map);
// // user input for origin, starting point


// // Establish location markers
// var marker = L.marker([-122.411497, 37.788913])
//     .addTo(map);

// // Establish pop ups
// var popup = L.popup();

// function onMapClick(e) {
//     popup
//         .setLatLng(e.latlng)
//         .setContent("You clicked the map at " + e.latlng.toString())
//         .openOn(mymap);
// }

// map.on('click', onMapClick);

// var markers = {
//     "type": "FeatureCollection",
//     "features": [{
//         "type": "Feature",
//         "properties": {
//             "description": "<div class=\"marker-title\">San Francisco</div><p>Even more info about San Francisco.</p>",
//             "marker-symbol": "theatre"
//         },
//         "geometry": {
//             "type": "Point",
//             "coordinates": [-122.411497, 37.788913]
//         }
//     }, {
//         "type": "Feature",
//         "properties": {
//             "description": "<div class=\"marker-title\">Coit Tower</div><p>So much descriptive copy about coitus tower and its history, maybe a picture too.</p>",
//             "marker-symbol": "theatre"
//         },
//         "geometry": {
//             "type": "Point",
//             "coordinates": [-122.4058044, 37.8024286]
//         }
//     }, {
//     "type": "Feature",
//     "properties": {
//         "description": "<div class=\"marker-title\">Bernal Heights</div><p>Windy and hilly hilltop for hipsters and new parents.</p>",
//         "marker-symbol": "theatre"
//     },
//     "geometry": {
//         "type": "Point",
//         "coordinates": [-122.417046, 37.744385]
//         }
//     }]
// };

// map.on('load', function() {
//     // Add marker data as a new GeoJSON source.
//     map.addSource("markers", {
//         "type": "geojson",
//         "data": markers
//     });

//     // Add a layer showing the markers.
//     map.addLayer({
//         "id": "markers",
//         "type": "symbol",
//         "source": "markers",
//         "layout": {
//             "icon-image": "{marker-symbol}-15",
//             "icon-allow-overlap": true
//         }
//     });
// });


// // Create a popup, but don't add it to the map yet.
// var popup = new mapboxgl.Popup({
//     closeButton: false,
//     closeOnClick: false
// });

// map.on('mousemove', function(e) {
//     var features = map.queryRenderedFeatures(e.point, { layers: ['markers'] });
//     // Change the cursor style as a UI indicator.
//     map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';

//     if (!features.length) {
//         popup.remove();
//         return;
//     }

//     var feature = features[0];

//     // Populate the popup and set its coordinates
//     // based on the feature found.
//     popup.setLngLat(feature.geometry.coordinates)
//         .setHTML(feature.properties.description)
//         .addTo(map);
// });

// function plotAddress(coordinates) {
//   console.log(coordinates);

// }

//     // with latlng from address, add marker on map, zoom in and show nearby
//     function findAddress(results) {
//       console.log(results);
//       $('#wait').css("display", "none");
//       if (results.status === "no found") {
//         alert("Not found! Try again.");
//         return "Not found! Try again.";
//       }
//       var lnglat = results.coordinates;
//       var addressLayer = L.mapbox.featureLayer().addTo(map);

//       var newMarker = {
//           type: 'Feature',
//           geometry: {
//             type: 'Point',
//             coordinates: lnglat
//           },
//           properties: {
//             'title': 'We found it! Click to explore',
//             'marker-color': '#F03C02',
//             'marker-symbol': 'pitch'
//           }
//         };

// $.get('/geocode', plotAddress);


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



