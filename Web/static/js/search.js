 $ = jQuery;

  var source = [{ value: "masan",
                 label: "Masan"
               },
               { value: "ABCD2",
                 label: "ABCD2"
               },
             ];

             $(document).ready(function() {
    $(".tags").autocomplete({
        source: source,
        select: function( event, ui ) { 
            url = "http://127.0.0.1:5000/movie/"+ ui.item.value;
            window.location = url;
        }
    });
});
