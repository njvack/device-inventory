// Generated by CoffeeScript 1.4.0
(function() {
  var checkout_selected, get_selected_id, get_selected_ids, initialize_table;

  initialize_table = function() {
    return $('#id_devices_table').dataTable({
      "sDom": "<'row-fluid'<'span6'T><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
      "oTableTools": {
        "sSwfPath": '/static/libs/datatables/extras/TableTools/media/swf/copy_csv_xls.swf',
        'sRowSelect': 'single',
        "aButtons": [
          {
            'sExtends': 'text',
            'sButtonClass': 'btn btn-large btn-primary btn-checkout',
            'sButtonText': '<i class="icon-signout"></i> Check OUT',
            'fnClick': function(nButton, oConfig, oFlash) {
              var ret;
              ret = prompt("Enter the lendee's name or subject ID: ", "");
              if (ret) {
                return checkout_selected(ret);
              }
            }
          }, {
            'sExtends': 'text',
            'sButtonClass': 'btn btn-large btn-warning btn-checkin',
            'sButtonText': '<i class="icon-signin"></i> Check IN'
          }, {
            'sExtends': 'text',
            'sButtonClass': 'btn btn-large btn-info btn-edit',
            'sButtonText': '<i class="icon-pencil"></i> Edit device'
          }, {
            'sExtends': 'csv',
            'sButtonClass': 'btn btn-large btn-default btn-export',
            'sButtonText': '<i class="icon-file"></i> Export'
          }
        ]
      }
    });
  };

  $(function() {
    window.oTable = initialize_table();
    return window.oTT = TableTools.fnGetInstance('id_devices_table');
  });

  checkout_selected = function(subject_id) {
    var selected;
    selected = oTT.fnGetSelected(oTable);
    return console.log(get_selected_id(selected));
  };

  get_selected_id = function(selected) {
    /*
        Returns the id of a selected device as an integer.
    */
    return $(selected).data('id');
  };

  get_selected_ids = function(selected) {
    /*
        Returns an array of ids for the selected devices.
    */
    return $.map(selected, function(element) {
      return $(element).data('id');
    });
  };

}).call(this);
