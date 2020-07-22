$('.ui.dropdown')
  .dropdown();
$('#dropdown').on('change', function() {
  console.log('before', $('#dropdown').val());
  $('#dropdown').val('a');
  console.log('after', $('#dropdown').val());
});
$(document).ready( function () {
  $('#dataTable').DataTable( {
    "language": {
      "sEmptyTable":      "Keine Daten in der Tabelle vorhanden",
      "sInfo":            "_START_ bis _END_ von _TOTAL_ Einträgen",
      "sInfoEmpty":       "Keine Daten vorhanden",
      "sInfoFiltered":    "(gefiltert von _MAX_ Einträgen)",
      "sInfoPostFix":     "",
      "sInfoThousands":   ".",
      "sLengthMenu":      "_MENU_ Einträge anzeigen",
      "sLoadingRecords":  "Wird geladen ..",
      "sProcessing":      "Bitte warten ..",
      "sSearch":          "Suchen",
      "sZeroRecords":     "Keine Einträge vorhanden",
      "oPaginate": {
          "sFirst":       "Erste",
          "sPrevious":    "Zurück",
          "sNext":        "Nächste",
          "sLast":        "Letzte"
      },
      "oAria": {
          "sSortAscending":  ": aktivieren, um Spalte aufsteigend zu sortieren",
          "sSortDescending": ": aktivieren, um Spalte absteigend zu sortieren"
      },
      "select": {
          "rows": {
              "_": "%d Zeilen ausgewählt",
              "0": "",
              "1": "1 Zeile ausgewählt"
          }
      },
      "buttons": {
          "print":    "Drucken",
          "colvis":   "Spalten",
          "copy":     "Kopieren",
          "copyTitle":    "In Zwischenablage kopieren",
          "copyKeys": "Taste <i>ctrl</i> oder <i>\u2318</i> + <i>C</i> um Tabelle<br>in Zwischenspeicher zu kopieren.<br><br>Um abzubrechen die Nachricht anklicken oder Escape drücken.",
          "copySuccess": {
              "_": "%d Spalten kopiert",
              "1": "1 Spalte kopiert"
          }
      }
  }
} );
} );
// Zu Wunderlist - Button
$(document).on('scroll', function() {
  var scrollDistance = $(this).scrollTop();
  if (scrollDistance > 10) {
    $('.btnwunderlist').fadeIn();
  }
});
//triggered when modal is about to be shown
$('#deleteModal').on('show.bs.modal', function(e) {

  //get data-id attribute of the clicked element
  var dish_id = $(e.relatedTarget).data('dish_id');

  //populate the textbox
  $(e.currentTarget).find('input[name="dish_id"]').val(dish_id);
});