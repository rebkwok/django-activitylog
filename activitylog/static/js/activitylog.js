//http://xdsoft.net/jqplugins/datetimepicker/
Date.parseDate = function( input, format ){
  return moment(input,format).toDate();
};
Date.prototype.dateFormat = function( format ){
  return moment(this).format(format);
};


jQuery(document).ready(function () {

    jQuery('#logdatepicker').datetimepicker({
        format:'DD-MMM-YYYY',
        formatTime:'HH:mm',
        timepicker: false,
        closeOnDateSelect: true,
        scrollMonth: false,
        scrollTime: false,
        scrollInput: false,
    });

});
