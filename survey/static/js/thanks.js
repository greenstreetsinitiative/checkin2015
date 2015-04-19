$(function() {
  $('#checkin-another').on('click', function(event) {
    event.preventDefault();
    simpleStorage.deleteKey('commutersurvey');
    window.location = '/commuterform';
  });
});