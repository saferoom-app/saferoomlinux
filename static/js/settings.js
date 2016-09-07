config = null;
default_onenote_notebook = ""
default_onenote_section = ""
$(document).ready(function(){
	$("[rel=tooltip]").tooltip({ placement: 'right'});

	// Loading the cache information
	CreateAJAX("/settings/cache","GET","json",{})
	.done(function(response){
		console.log(response);
		for (var key in response){
			$("td#cache_"+key).html(response[key]);
		}
	})
	.fail(function(xhr){

	});	

	// Loading the config
	CreateAJAX("/settings/config","GET","json",{})
	.done(function(response){
		// Processing the response
		config = response;

		$("select#txtDefaultService").val(response.system.default_service)
		$("select#evernoteStatus").val(response.evernote.status ? "1" : "0");
		if (response.evernote.token.status){
			$("div#evernoteToken").html("<span class=\"label label-success\">OK</span>");
		}
		else{
			$("div#evernoteToken").html("<span style=\"font-size:1em\" class=\"label label-danger\">"+response.evernote.token.message+"</span>");
		}

		// Setting default tags (if any)
		array = response.evernote.default_tags.split(",");
		if (array.length > 0){
			for (i=0;i<array.length;i++){
				$("input#txtTags").tagsinput('add',array[i]);
			}
		}

		$("select#onenoteStatus").val(response.onenote.status ? "1" : "0");
		if (response.onenote.client_id.status){
			$("div#onenoteClientID").html("<span class=\"label label-success\">OK</span>");
		}
		else{
			$("div#onenoteClientID").html("<span style=\"font-size:1em\" class=\"label label-danger\">"+response.onenote.client_id.message+"</span>");
		}
		if (response.onenote.client_secret.status){
			$("div#onenoteclientSecret").html("<span class=\"label label-success\">OK</span>");
		}
		else{
			$("div#onenoteclientSecret").html("<span style=\"font-size:1em\" class=\"label label-danger\">"+response.onenote.client_secret.message+"</span>");
		}

		$("input#txtRedirectURI").val(response.onenote.redirect_uri);
		$("input#txtScopes").val(response.onenote.scopes);
	})
	.fail(function(xhr){
		console.log(xhr.responseText)
	})

	// Loading a list of notebooks
	select_notebooks({})	

	// Loading a list of notebooks
	select_onenote_notebooks({})

	// Attaching click handler to all buttons in the table
	var td = null;
	$("table#tblCache").find("button").click(function(){

		// Displaying progress
        td = $(this).parent().parent().find("td[id='cache_"+this.id+"']");
        td.html("<img src=\"/static/images/103.gif\"/>");

		CreateAJAX("/settings/clear","GET","json",{type:this.id})
		.done(function(response){
			td.html("0B");
		})
		.fail(function(xhr){
			td.html(xhr.responseText);			
		});
	});

});

$(document).on("click","button#btnRefreshNotebooks",function(){
	select_notebooks({"refresh":true});
});
$(document).on("click","button#btnRefreshONNotebooks",function(){
	select_onenote_notebooks({"refresh":true});
});
$(document).on("click","button#btnRefreshSections",function(){
	select_sections($("select#txtONNotebook").val(),{"refresh":true});
});
$(document).on("change","select#txtONNotebook",function(){
	select_sections($("select#txtONNotebook").val(),{"refresh":true});
});
$(document).on("click","button#btnSave",function(){
	config = {}
	config['services'] = {}
	config['uris'] = {}
	config['defaults'] = {}

	// Getting system information
	config['defaults']['default_service'] = $("select#txtDefaultService").val();
	
	// Getting Evernote parameters
	config['services']['evernote'] = $("select#evernoteStatus").val();
	config['defaults']['default_evernote_notebook'] = $("select#txtNotebook").val();
	config['defaults']['default_tags'] = $("input#txtTags").val();

	// Getting Onenote parameters
	config['services']['onenote'] = $("select#onenoteStatus").val();
	config['defaults']['default_onenote_notebook'] = $("select#txtONNotebook").val();
	config['defaults']['default_onenote_section'] = $("select#txtSection").val();
	config['uris']['redirect_uri'] = $("select#txtRedirectURI").val();


	// Getting
	CreateAJAX("/settings/save","POST","json",{"config":JSON.stringify(config)})
	.done(function(response){
		showAlert(true,LEVEL_SUCCESS,response.message);
		scrollTop();
	})
	.fail(function(xhr){
		showAlert(true,LEVEL_DANGER,parse_json_response(xhr.responseText));
		scrollTop();
	});
});