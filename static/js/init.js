// Getting service status
CreateAJAX("/settings/services","GET","json",{})
.done(function(response){
	$("#iconOnenote").toggle(response.onenote);
	$("#iconEvernote").toggle(response.evernote);
})
.fail(function(xhr){
	alert(xhr.responseText);
})

// Checking Onenote Access Token status
CreateAJAX("/onenote/token/check","GET","json",{})
.done(function(response){
	showToast(LEVEL_WARN,MSG_TOKEN_UPDATE);
	update_access_token(response.token);
})
.fail(function(xhr){
	return false;
});