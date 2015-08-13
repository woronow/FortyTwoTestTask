var helloRequest = (function($){

  function handleRequest(data) {
    var items = ['<thead><tr><th>Path</th>\
                 <th>Method</th><tr></thead>'];
    var j_data = $.parseJSON(data);
    var id = 0;
    $.each(j_data, function(i, val) {
      id += parseInt(val.fields.new_request, 10);
      if (i < 10 ){
        items.push('<tr id="' + val.pk + '">'
                   + '<td>' + val.fields.path + '</td>'
                   + '<td>'+ val.fields.method + '</td>'
                   + '</tr>');

    }
   });
   var title = $('title').text().split('-')[1] || $('title').text();
   var pre_titile = id ? id + '-' : '';
   $('#request').html(items);
   $('title').text(pre_titile + title);
 }

 return {
     loadRequest: function(){
         $.ajax({
             url: '/request_ajax/',
             dataType : "json",
             success: function (data, textStatus) {
                 handleRequest(data);
             }
         });
     }
 };
})(jQuery);


$(document).ready(function(){
    helloRequest.loadRequest();
    setInterval(helloRequest.loadRequest, 10000);
});