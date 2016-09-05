$(document).ready(function(){
	$("[rel=tooltip]").tooltip({ placement: 'right'});

	$("button#btnStart").click(function(){

        if ($("input#txtPassword").val() == ""){
        	$("input#txtPassword").focus();
        	return;
        }

        if ($("input#txtConfPassword").val() != $("input#txtPassword").val() ){
        	alert("Passwords don't match. Please try again");
        	$("input#txtPassword").focus();
        	return;
        }

		config = {}
		config['services'] = {}
		config['uris'] = {}
		config['defaults'] = {}
		config['tokens'] = {}

		// Getting system information
		config['defaults']['default_service'] = "0";

		// Setting tokens
		config['tokens']['evernote_developer'] = $("input#txtDeveloperToken").val();
		config['tokens']['client_id'] = $("input#txtClientID").val();
		config['tokens']['client_secret'] = $("input#txtClientSecret").val();

		// Getting Evernote parameters
		config['services']['evernote'] = $("select#txtStatus_en").val();
		config['defaults']['default_evernote_notebook'] = "";
		config['defaults']['default_tags'] = "";

		// Getting Onenote parameters
		config['services']['onenote'] = $("select#txtStatus_on").val();
		config['defaults']['default_onenote_notebook'] = "";
		config['defaults']['default_onenote_section'] = "";
		config['uris']['redirect_uri'] = $("input#txtRedirectUri").val();

		displayProgress(MSG_CONFIG_SAVE,true);
		// Getting
		CreateAJAX("/settings/save","POST","json",{"config":JSON.stringify(config),"pass":$("input#txtPassword").val()})
		.done(function(response){
			displayProgress("",false);
			if (response.status != HTTP_OK){
				showAlert(true,LEVEL_DANGER,response.message);
				return;
			}
			location.href = "/";
		})
		.fail(function(xhr){
			displayProgress("",false);
			showAlert(true,LEVEL_DANGER,xhr.responseText);
		});

	});
});