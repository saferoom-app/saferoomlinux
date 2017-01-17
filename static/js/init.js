// Getting service status
CreateAJAX("/settings/services","GET","json",{})
.done(function(response){
	console.log(response);
	$("#iconOnenote").toggle(response.services.onenote);
	$("#iconEvernote").toggle(response.services.evernote);
	if (response.master == false){
		showToast(LEVEL_WARN,MSG_NO_PASSWORD);
	}
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