$(function() {
  //activate chosen plugin
  $("#id_employer, #id_team").chosen({
    width: "99%"
  });

  // show message for those running IE 7 or lower
  var isIE = document.all && !document.querySelector;
  if (isIE) {
    $('.browser').show();
  } else {
    $('.browser').hide();
  }

  var $employerSelect = $('select[name="employer"]');
  var $subteamSelect = $('select[name="team"]');

  $employerSelect.on('checkin:setsubteams', setSubteamToggling());
  $employerSelect.trigger('chosen:updated').trigger('checkin:setsubteams');

  $employerSelect.on('change', function() {
    $subteamSelect.val('').trigger('chosen:updated'); // reset the subteam form
    setSubteamToggling();
  });

  function setSubteamToggling(event) {
    // hide or show the other dropdown
    var parentid = $employerSelect.find(':selected').val();
    var allParentIDs = $.map($subteamSelect.find('option'), function(opt) { return $(opt).attr('data-parent') });
    var employerHasSubteam = jQuery.inArray(parentid, allParentIDs) > 0;

    if (employerHasSubteam) {
      // show the select element with only the relevant options
      $subteamSelect.find('option').each(function(){
        if ($(this).attr('data-parent') == parentid) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
      $subteamSelect.chosen('destroy').chosen({ width: "99%" });

      $subteamSelect.parent().parent().show();
    } else {
      $subteamSelect.parent().parent().hide();
    }
  }

  $subteamSelect.on('change', function() {
    var subteamValueChosen = $subteamSelect.val() !== '';
    if (subteamValueChosen && $('.team-alert')) {
      $('.team-alert').remove();
    }
  });

  var $normalFWLegs = $('.normal-day .from-work .legs-wrapper');
  var $normalTWLegs = $('.normal-day .to-work .legs-wrapper');
  var $walkrideFWLegs = $('.wr-day .from-work .legs-wrapper');
  var $walkrideTWLegs = $('.wr-day .to-work .legs-wrapper');

  // activate formset plugin for the 4 formsets
  $normalFWLegs.find('.leggedrow').formset({
      prefix: 'nfw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-nfw-form',
      keepFieldValues: 'input[type="hidden"][name^="nfw"]'
  });
  $normalTWLegs.find('.leggedrow').formset({
      prefix: 'ntw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-ntw-form',
      keepFieldValues: 'input[type="hidden"][name^="ntw"]'
  });
  $walkrideFWLegs.find('.leggedrow').formset({
      prefix: 'wfw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-wfw-form',
      keepFieldValues: 'input[type="hidden"][name^="wfw"]'
  });
  $walkrideTWLegs.find('.leggedrow').formset({
      prefix: 'wtw',
      addText: 'Add more segments',
      deleteText: 'Remove this segment',
      formCssClass: 'dynamic-wtw-form',
      keepFieldValues: 'input[type="hidden"][name^="wtw"]'
  });

  // don't let people delete that first leg!! trick by making the link invisible!
  $('.legs-wrapper .leggedrow:first-of-type .delete-row:first-of-type').css('visibility','hidden');

  var $walkrideSameBothWaysRadio = $('[name="walkride_same_as_reverse"]');
  var $normalEqualsWalkrideRadio = $('[name="normal_same_as_walkride"]');
  var $normalSameBothWaysRadio = $('[name="normal_same_as_reverse"]');

  // handles options for if walkride day's commute FROM work is same as TO work
  $walkrideSameBothWaysRadio
    .on('checkin:initialize', function(event) {
      if (shouldOpen($walkrideSameBothWaysRadio)) {
        $walkrideFWLegs.show();
      } else {
        $walkrideFWLegs.hide();
      }
    })
    .on('change', function() {
      if (shouldOpen($walkrideSameBothWaysRadio)) {
        $walkrideFWLegs.show();
      } else {
        // on closing, should copy other form
        $walkrideFWLegs.hide();
        $walkrideSameBothWaysRadio.trigger('checkin:copyleg');
      }
    });

  // handles options for if the normal commute happens to be the same as the walk-ride day commute
  $normalEqualsWalkrideRadio
    .on('checkin:initialize', function(event) {
      if (shouldOpen($normalEqualsWalkrideRadio)) {
        $('.normal-legs').show();
      } else {
        // on closing, should copy other form
        $('.normal-legs').hide();
      }
    })
    .on('change', function() {
      if (shouldOpen($normalEqualsWalkrideRadio)) {
        $('.normal-legs').show();
      } else {
        // on closing, should copy other form
        $('.normal-legs').hide();
        $normalEqualsWalkrideRadio.trigger('checkin:copyleg');
      }
    });

  // handles options for if normal day's commute FROM work is same as TO work
  $normalSameBothWaysRadio
    .on('checkin:initialize', function(event) {
      if (shouldOpen($normalSameBothWaysRadio)) {
        $normalFWLegs.show();
      } else {
        // on closing, should copy other form
        $normalFWLegs.hide();
      }
    })
    .on('change', function() {
      if (shouldOpen($normalSameBothWaysRadio)) {
        $normalFWLegs.show();
      } else {
        // on closing, should copy other form
        $normalFWLegs.hide();
        // only copy this if normal legs arent expected
        // to be equal to wr-day legs
        if (shouldOpen($normalEqualsWalkrideRadio)) {
          $normalSameBothWaysRadio.trigger('checkin:copyleg');
        }
      }
    });


  $walkrideSameBothWaysRadio.on('checkin:copyleg', function(event) {
    copyLegData($walkrideTWLegs, $walkrideFWLegs);
  });
  $normalEqualsWalkrideRadio.on('checkin:copyleg', function(event) {
    copyLegData($walkrideTWLegs, $normalTWLegs);
    copyLegData($walkrideFWLegs, $normalFWLegs);
  });
  $normalSameBothWaysRadio.on('checkin:copyleg', function(event) {
    copyLegData($normalTWLegs, $normalFWLegs);
  });

  // trigger the hiding/showing
  $walkrideSameBothWaysRadio.trigger('checkin:initialize');
  $normalEqualsWalkrideRadio.trigger('checkin:initialize');
  $normalSameBothWaysRadio.trigger('checkin:initialize');

  $('form').submit(function(e) {
    // if any of the radio buttons say true, and were
    // not actually changed, we need to still copy the forms
    // trigger the copying only
    $walkrideSameBothWaysRadio.trigger('change');
    $normalEqualsWalkrideRadio.trigger('change');
    $normalSameBothWaysRadio.trigger('change');

    var subteamVisible = $('#id_team_chosen').is(':visible');
    var subteamValueChosen = $subteamSelect.val() !== '';

    if (subteamVisible && !subteamValueChosen) {
      $('button[type="submit"]').before('<div class="alert alert-danger team-alert" role="alert">Your company has sub-teams! Please indicate your team affiliation above.</div>');
      return false;
    } else {
      return true;
    }
  });

  function shouldOpen(selector) {
    // returns true or false
    return selector.filter(':checked').val() == "False";
  }

  function clearLegData(selector) {
    var $legs = $(selector).find('.leggedrow'); //legs
    var $durations = $legs.find('input[name$="duration"]'); //durations
    var $modes = $legs.find('select[name$="mode"]'); //modes
    $durations.val('');
    $modes.val('').trigger('change');
  }

  function copyLegData($originalForm, $newForm) {
    clearLegData($newForm);
    var $originalLegs = $originalForm.find('.leggedrow');
    // click 'add' or 'remove' until right number of legs
    var extraLegs = $originalLegs.length - $newForm.find('.leggedrow').length;
    if (extraLegs > 0) {
      // add legs
      for (var i = 0; i < extraLegs; i++) {
        $newForm.find('.add-row').trigger('click');
        console.log('added hidden leg');
      }
    } else if (extraLegs < 0) {
      // remove legs
      for (var i = 0; i < -1*extraLegs; i++) {
        $newForm.find('.delete-row').last().trigger('click');
        console.log('removed hidden leg');
      }
    }

    // copying the values
    $originalLegs.each(function(index, leg) {
      var $originalLeg = $(leg);
      var originalDuration = $originalLeg.find('input[name$="duration"]').val();
      var originalMode = $originalLeg.find('select[name$="mode"]').val();
      var $newLeg = $newForm.find('.leggedrow').eq(index);
      $newLeg.find('input[name$="duration"]').val(originalDuration);
      $newLeg.find('select[name$="mode"]').val(originalMode);
    });
  }

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
