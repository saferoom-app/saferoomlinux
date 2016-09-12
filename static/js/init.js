// Getting service status
CreateAJAX("/settings/services","GET","json",{})
.done(function(response){
	$("#iconOnenote").toggle(response.onenote);
	$("#iconEvernote").toggle(response.evernote);
})
.fail(function(xhr){
	alert(xhr.responseText);
})