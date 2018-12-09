var uploadInfo = $("#upload-info");
uploadInfo[0].addEventListener("animationend",function(){$(this).css("animation","");});
$(function(){
	$("#upload-form").ajaxForm(function(data){  
		if(data){
		    uploadInfo.show();
		    uploadInfo.css({"animation":"1s ease-in-out 0s 2 normal none running flicker-s"});
	 	    uploadInfo[0].className="alert alert-success";
		    uploadInfo[0].innerHTML="File has been uploaded successfully!"
			
		    window.location.replace("?F="+data) 
		}
	});     
});

var inputfile = $("input[name='file']")[0];
inputfile.addEventListener( 'change', function( e ){
    var sp = $("#label-upload").children()[0];
    sp.textContent = inputfile.files[0].name;
});
var judge = function(){
        if (getFileSize("file") == 0){
		uploadInfo.show();
		uploadInfo.css({"animation":"1s ease-in-out 0s 3 normal none running flicker"});
                uploadInfo[0].className="alert alert-danger";
                uploadInfo[0].innerHTML="Please choose one file";
		return false;}
        else if (getFileSize("file") > 10){
		uploadInfo.show();
		uploadInfo.css({"animation":"1s ease-in-out 0s 3 normal none running flicker"});
		uploadInfo[0].className="alert alert-danger";
                uploadInfo[0].innerHTML="File size must not exceed 10M";
		return false;}
        else{return true;}};

        function getFileSize(eleName) {
                var size = 0;
                if(inputfile.files.length != 0){
			size = inputfile.files[0].size;
                        size = size / 1024;//kb
                        size = size / 1024;//mb
                        return size;}
                else {return size;}
        };

$(function() {var r = 0;
            $(document.getElementById('gly-ej')).click(function() {
            r += 180;$(this).css('transform', 'rotate(' + r + 'deg)');});});
        tick = function(){ 
        document.getElementsByClassName('bk-cb')[0].firstChild.firstChild.click();}

var cross = function(){
(function ($) {
	"use strict";
	$('.column100').on('mouseover',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).addClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).addClass('hov-column-head-'+ verTable);
	});

	$('.column100').on('mouseout',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).removeClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).removeClass('hov-column-head-'+ verTable);
	});
})(jQuery);};

var s=0;
var e=10;
var batch=10;
var pt = $("#pair-data");
get_pd = function(){$.ajax({
  url: $("meta")[1].content+"/pair_data",
  type: "GET",
  data: {'s':s, 'e':e},
  success: function (response){
    var i=1;
    var pair_data = $.parseJSON(response);
    for (key in pair_data){
      if (s==0){
      pt.children("thead").children("tr").append('<th class="column100 column'+i+'" data-column="column'+i+'">'+key+'</th>');
      };
      var ii=1+s;
      for (v in pair_data[key]){
	if (i==1){
	pt.children("tbody").append('<tr class="row100"></tr>');};
	pt.children("tbody").children("tr")[ii-1].innerHTML +='<td class="column100 column'+i+'" data-column="column'+i+'">'+pair_data[key][v]+'</td>';
	ii++;}i++;};cross();$('#lds-roller').hide();s=e;e=s+batch;},
  error: function (response){console.log('error')}
})};

get_pd();
var sT = 0;
$(".panel-body").scroll(function () {
    var scrollTop = $(this).scrollTop();
    var h = $(this).outerHeight();
    var th = $(".container-table100").height();
    if (scrollTop+h>th & Math.abs(scrollTop-sT)>20) {
	$('#lds-roller').show();
        console.log(scrollTop+' bottom!');
	get_pd();
	sT = scrollTop;
       }
   });

