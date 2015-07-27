$(function() {
  //activate chosen plugin
  $("#id_employer").chosen({
    width: "99%"
  });

  // show message for those running IE 7 or lower
  var isIE = document.all && !document.querySelector;
  if (isIE) {
    $('.browser').show();
  } else {
    $('.browser').hide();
  }

  //make subteam dropdown required only when there are subteams populated
  $('#id_team').parent().parent().hide();

  $('#validation1, #validation2, #confirmation').hide();

  $('button[type="submit"]').prop('disabled', true);

  // enable the submit button only when stuff is filled in!
  stuff = 'input[name="email"], input[name="home_address"], input[name="work_address"], select[name="employer"], select[name="team"]:visible, input[name$="duration"]:visible, select[name$="mode"]:visible';

  $('form').on('change', stuff, function(){
    $('#confirmation').hide();
    // check if legs are filled
    empty_legs = $('input[name$="duration"]:visible, select[name$="mode"]:visible').filter(function(el){ return $(this).val() === ""; });
    // check if other required fields are filled
    empty_required_fields = $('input[name="email"], input[name="home_address"], input[name="work_address"], select[name="employer"], select[name="team"]:visible').filter(function(el){ return $(this).val() === ""; });

    if (empty_legs.length > 0) {
      $('#validation2').text('Please make sure all parts of all segments on the screen are filled out.').show();
    }

    if (empty_required_fields.length > 0) {
      $('#validation1').text('Please check-in with your email address, two addresses, employer, and your team if applicable.').show();
    }

    if (empty_required_fields.length + empty_legs.length == 0) {
      $('#validation1, #validation2').hide();
      $('#confirmation').show();
      $('button[type="submit"]').removeAttr('disabled');
    }
  });

  $(document).ajaxSuccess(function() {
    // the subteams get populated via ajax which triggers here
    if ($('#id_team').find('option').length > 1) {
      $('#id_team').prop('required', true);
      $('#id_team').parent().parent().show()
    } else {
      $('#id_team').prop('required', false);
      $('#id_team').parent().parent().hide()
    }
  });

  // activate formset plugin for the 4 formsets
  $(' .normal-day .from-work .legs-wrapper .leggedrow').formset({
      prefix: 'nfw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-nfw-form',
      keepFieldValues: 'input[type="hidden"][name^="nfw-0-d"]'
  });
  $('.normal-day .to-work .legs-wrapper .leggedrow').formset({
      prefix: 'ntw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-ntw-form',
      keepFieldValues: 'input[type="hidden"][name^="ntw-0-d"]'
  });
  $('.wr-day .from-work .legs-wrapper .leggedrow').formset({
      prefix: 'wfw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-wfw-form',
      keepFieldValues: 'input[type="hidden"][name^="wfw-0-d"]'
  });
  $('.wr-day .to-work .legs-wrapper .leggedrow').formset({
      prefix: 'wtw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-wtw-form',
      keepFieldValues: 'input[type="hidden"][name^="wtw-0-d"]'
  });

  // don't let people delete that first leg!! trick by making the link invisible!
  $('.legs-wrapper .leggedrow:first-of-type .delete-row:first-of-type').css('visibility','hidden')

  // hide extra leg stuff at first
  $('.wr-day .from-work .legs-wrapper').hide();
  $('.normal-legs').hide();
  $('.normal-day .from-work .legs-wrapper').hide();

  function clearLegData(selector) {
    var $legs = $(selector).find('.leggedrow'); //legs
    var $durations = $legs.find('input[name$="duration"]'); //durations
    var $modes = $legs.find('select[name$="mode"]'); //modes
    $durations.val('');
    $modes.val('').trigger('change');
    $legs.find('.delete-row').each(function(){
      if ($(this).css("visibility") != "hidden") { $(this).trigger('click'); } //deletes extra blank legs
    });
  }

  // handles options for if walkride day's commute FROM work is same as TO work
  $('#id_walkride_same_as_reverse input:radio').change(function() {
    $('.wr-day .from-work .legs-wrapper').toggle({ start: function() {
      if ($(this).is(':visible')) { clearLegData($(this)); }}
    });
  });

  // handles options for if the normal commute happens to be the same as the walk-ride day commute
  $('#id_normal_same_as_walkride input:radio').change(function() {
    $('.normal-legs').toggle({ start: function() {
      if ($(this).is(':visible')) { clearLegData($(this)); }}
    });
  });

  // handles options for if normal day's commute FROM work is same as TO work
  $('#id_normal_same_as_reverse input:radio').change(function() {
    $('.normal-day .from-work .legs-wrapper').toggle({ start: function() {
      if ($(this).is(':visible')) { clearLegData($(this)); }}
    });
  });

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
