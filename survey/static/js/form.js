$(function() {
  //activate chosen plugin
  $("#id_employer, #id_team").chosen({
    width: "99%"
  });

  // show message for those running IE 7 or lower
  var isIE = document.all && !document.querySelector;
  $('.browser').toggle(isIE);

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
        $(this).toggle($(this).attr('data-parent') == parentid);
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
      $walkrideFWLegs.toggle(shouldOpen($walkrideSameBothWaysRadio));
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
        $('.normal-legs').toggle(shouldOpen($normalEqualsWalkrideRadio));
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
        $normalFWLegs.toggle(shouldOpen($normalSameBothWaysRadio));
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

  //////////
  // if legs were filled in previously, fill them in again here.
  // savedLegs is defined in the new_checkin.html template
  if (savedLegs['wtw']['durations'].length > 0) {
    fillSavedLegs(savedLegs['wtw'], $walkrideTWLegs);

    // if (savedLegs['wfw'] == savedLegs['wtw']) {
    if (_.isEqual(savedLegs['wfw'], savedLegs['wtw'])) {
      $walkrideSameBothWaysRadio.val(['True']).trigger('change');
    } else {
      $walkrideSameBothWaysRadio.val(['False']).trigger('change');
      fillSavedLegs(savedLegs['wfw'], $walkrideFWLegs);
    }

    if (_.isEqual(savedLegs['ntw'], savedLegs['wtw'])) {
      $normalEqualsWalkrideRadio.val(['True']).trigger('change');
    } else {
      $normalEqualsWalkrideRadio.val(['False']).trigger('change');
      fillSavedLegs(savedLegs['ntw'], $normalTWLegs);

      if (_.isEqual(savedLegs['nfw'], savedLegs['ntw'])) {
        $normalSameBothWaysRadio.val(['True']).trigger('change');
      } else {
        $normalSameBothWaysRadio.val(['False']).trigger('change');
        fillSavedLegs(savedLegs['nfw'], $normalFWLegs);
      }
    }
  }
  //////////

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

  // takes an object and applies its information to the element
  function fillSavedLegs(info, $element) {
    var numLegs = info['durations'].length;
    var modeSelect = 'select[name$="mode"]:last';
    var durationInput = 'input[name$="duration"]:last';

    for (var i = 0; i < numLegs; i++) {
      $element.find(modeSelect).val(info['modes'][i]);
      $element.find(durationInput).val(info['durations'][i]);
      if (i+1 < numLegs) { $element.find('a.add-row').click() }
    }
  }
});
