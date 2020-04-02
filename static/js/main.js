$('.ui.dropdown')
  .dropdown();
$('#dropdown').on('change', function() {
  console.log('before', $('#dropdown').val());
  $('#dropdown').val('a');
  console.log('after', $('#dropdown').val());
});