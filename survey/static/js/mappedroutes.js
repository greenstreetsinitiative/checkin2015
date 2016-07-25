$(function() {
  // do all this stuff for geocoding
  var geocoder = new google.maps.Geocoder();
  var position1, position2, marker1, marker2;

  function geocodeAddress($address) {
    geocoder.geocode({address: $address.val()}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        $address.val(results[0]['formatted_address']);

        if ($address.attr('id') == "id_home_address") {
          position1 = results[0].geometry.location;

          if (marker1) {
            marker1.setMap(null);
          }

          marker1 = new google.maps.Marker({
                     map: map,
                     title: results[0]['formatted_address'],
                     position: results[0].geometry.location,
                     animation: google.maps.Animation.DROP
                   });
        } else if ($address.attr('id') == "id_work_address") {
          position2 = results[0].geometry.location;

          if (marker2) {
            marker2.setMap(null);
          }

          marker2 = new google.maps.Marker({
                     map: map,
                     title: results[0]['formatted_address'],
                     position: results[0].geometry.location,
                     animation: google.maps.Animation.DROP
                   });
        }

        map.panTo(results[0].geometry.location);

        if (position1 && position2) {
          setCommuteGeom(position1, position2);
          setCommuteGeom2(position1, position2);
          setCommuteGeom3(position1, position2);
        }
      }
    });


  }

  function setCommuteGeom(origin, destination) {
    directionsService.route({
      origin: origin,
      destination: destination,
      travelMode: google.maps.TravelMode.BICYCLING
    }, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setMap(map);
        directionsDisplay.setDirections(response);
        toggleCommuteDistance(response.routes[0].legs[0].distance.text + ' (by bike)');
        } else {
        toggleCommuteDistance('');
      }
    });
  }

  function setCommuteGeom2(origin, destination) {
    directionsService2.route({
      origin: origin,
      destination: destination,
      travelMode: google.maps.TravelMode.TRANSIT
    }, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay2.setMap(map);
        directionsDisplay2.setDirections(response);
        toggleCommuteDistance2(response.routes[0].legs[0].distance.text + ' (by transit)');
      } else {
        toggleCommuteDistance2('');
         }
       });
     }

  function setCommuteGeom3(origin, destination) {
    directionsService3.route({
      origin: origin,
      destination: destination,
      travelMode: google.maps.TravelMode.WALKING
    }, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay3.setMap(map);
        directionsDisplay3.setDirections(response);
        toggleCommuteDistance3(response.routes[0].legs[0].distance.text + ' (by foot)');
      } else {
        toggleCommuteDistance3('');
      }
    });
  }

  function toggleCommuteDistance(text) {
    if (text !== '') {
      $('#commute-distance').text(text);
      $('#commute-distance').css('background', '#77C5F1');
    } else {
      $('#commute-distance').text('');
      $('#commute-distance').css('background', '#fff');
    }
  }

  function toggleCommuteDistance2(text) {
    if (text !== '') {
      $('#commute-distance2').text(text);
      $('#commute-distance2').css('background', '#CDAAFF');
    } else {
      $('#commute-distance2').text('');
      $('#commute-distance2').css('background', '#fff');
    }
  }

  function toggleCommuteDistance3(text) {
    if (text !== '') {
      $('#commute-distance3').text(text);
      $('#commute-distance3').css('background', '#FF9966');
    } else {
      $('#commute-distance3').text('');
      $('#commute-distance3').css('background', '#fff');
    }
  }

  function pathToGeoJson(path) {
    if (path.length <= 1) {
      // point if home and work location are the same;
      // empty coordinates is a valid MultiLineString in GEOS,
      // only one coordinate is not
      return { type: 'MultiLineString', coordinates: [] };
    } else {
      return {
        type: 'MultiLineString',
        coordinates: [
          $.map(path, function(v,i) {
            return [[v.lng(), v.lat()]];
          })
        ]
      };
    }
  }

  // trigger address geocoder on several UI interactions
  $('#id_home_address, #id_work_address').on('keyup', function(event) {
    if (event.which === 13) geocodeAddress($(this));
  });
  $('#id_home_address, #id_work_address').on('blur', function(event) {
    geocodeAddress($(this));
  });

  //trigger initial blur to show pre-filled addresses on the map
  $('#id_home_address, #id_work_address').trigger('blur');

  var directionsService, directionsDisplay,
      directionsService2, directionsDisplay2,
      directionsService3, directionsDisplay3;

  directionsService = new google.maps.DirectionsService();
  directionsService2 = new google.maps.DirectionsService();
  directionsService3 = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer({
    markerOptions: {
      visible: false
    }
  });
  directionsDisplay2 = new google.maps.DirectionsRenderer({
    markerOptions: {
      visible: false
    },
    polylineOptions: {
      strokeColor: '#CDAAFF'
    }
  });
  directionsDisplay3 = new google.maps.DirectionsRenderer({
    markerOptions: {
      visible: false
    },
    polylineOptions: {
      strokeColor: '#FF9966'
    }
  });

  map = new google.maps.Map(document.getElementById('map-canvas'), {
    zoom: 11,
    mapTypeId: google.maps.MapTypeId.TERRAIN,
    center: new google.maps.LatLng(42.357778, -71.061667),
    streetViewControl: false,
    mapTypeControl: false
  });
});
