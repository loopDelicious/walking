// default mapbox.js API public access token
L.mapbox.accessToken = 'pk.eyJ1Ijoiam95Y2VsaW43OSIsImEiOiJjaW8zNzk5bHcwMDA5dzFrcXd6anpnY2xoIn0.ovObS9ODfNsnaa8ie--fKQ';

var latlng = [37.7749, -122.4194]

// load base map of San Francisco
var map = L.mapbox.map('map', 'mapbox.dark', {
    accessToken: L.mapbox.accessToken,
    zoomControl: false,
    attributionControl: false,
    zoom: 12,  // starting zoom
    minZoom: 9, // farthest you can zoom out
    maxZoom: 16,  // closest you can zoom in
    center: latlng,  // starting position to center map on SF
    interactive: false, // make interactive
    });

// load the saved markers into a featureLayer from geojson, and add to map
var savedLayer = L.mapbox.featureLayer().addTo(map);
savedLayer.loadURL('/saved.geojson');



// create popups for landmarks
savedLayer.on('layeradd', function(e) {

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
        '<h2><a href="/landmarks/' + feature.id + '" class="thumbnail"><img src="' + feature.image + '" />' + 
        feature.properties.name + '</a></h2><p>' + feature.properties.description + '</br>Average Rating: ' + 
        feature.avg_rating + '</p>';
                        
    marker.bindPopup(popupContent, {
        closeButton: true,
        minWidth: 120,
        zoomAnimation: true,
        fadeAnimation: true,
        autoPan: true,
    });
});

// display popups on click, and close popups on mouseout
savedLayer.on('click', function(e) {
    e.layer.openPopup();
});

// disable zoom and panning
map.dragging.disable();
map.touchZoom.disable();
map.doubleClickZoom.disable();
map.scrollWheelZoom.disable();
map.keyboard.disable();

$('.clear').on('click', function(e) {
  e.preventDefault();
  var $this = $(this);
  $.ajax({
    type: "POST",
    url: '/clear_walk',
    data: {
      'walk_id': $this.data('value')
    },
    success: function(response) {
      if (response=="Walk deleted.") {
        bootbox.alert("Walk removed.");
        $this.parent().remove();
      }
    }
  });
});

$('.clear-saved').on('click', function(e) {
  e.preventDefault();
  var $this = $(this);
  $.ajax({
    type: "POST",
    url: '/clear_a_saved',
    data: {
      'saved_id': $this.data('value')
    },
    success: function(response) {
      if (response=="Saved landmark deleted.") {
        bootbox.alert("Landmark removed.");
        // remove display from DOM 
        $this.parent().remove();
      }
    }
  });
});