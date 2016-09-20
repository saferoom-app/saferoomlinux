// Path object to generate links
path = new Array();
var FINISHED = false;
/*
	Global variables section
*/

// HTML templates
TPL_ATTACH = "<div class=\"attachment\"><div class=\"row\"><div class=\"col-md-10\" style=\"display:inline-block\"><span style=\"margin-left:10px\"><img src=\"/static/images/::fileicon::\"/></span><span style=\"margin-left:10px\"><a href=\"/tmp/::filename::\">::filename:: (Size: ::filesize::)</a></span><span id='enml'><en-media data-type=\"::filetype::\" data-hash=\"::filehash::\" data-filename=\"::filename::\"/></span></div><div class=\"col-md-2\"><span id='txtFilename' style='display:none'>::filename::</span><span class=\"pull-right\" style=\"margin-right:10px\"><span id='removeAttach' class=\"glyphicon glyphicon-remove link\" aria-hidden=\"true\"></span></span></div></div></div><br/>";
TPL_IMAGE_ATTACH = "<img class='attach' style='max-width:70%;max-height=70%' data-type='::fileType::' data-filename='::filename::' data-hash='::filehash::' src=\"/static/tmp/::filename::\"/>";
TPL_PAGE_ENCRYPTED = "<div class='row'><div class='col-md-12' style='text-align:center;padding:30px 30px 30px 30px'><div><img src='/static/images/::icon::'></div><div class='greyedText'>This ::pageType:: is encrypted. To see its contents, please decrypt it</div></div></div>"
tpl_select_disabled = "<select id=\"::id::\" class='form-control' style='width:70%'><option value=''>::message::</option></select>";

// Type of alerts
LEVEL_INFO = 0;
LEVEL_SUCCESS = 1;
LEVEL_WARN = 2;
LEVEL_DANGER = 3;

// Service IDs
service_evernote = 0
service_onenote = 1

// Common system messages
MSG_INTERNAL_ERROR = "Server internal error. Please check system logs";
MSG_NOTE_UPLOAD = "Encrypting and uploading note ... Please wait";
MSG_NOTEBOOKS_LOAD = "Loading a list of notebooks ... Please wait";
MSG_TAGS_LOAD = "Loading a list of tags ... Please wait";
MSG_SEARCHES_LOAD = "Loading a list of Saved Searches ... Please wait";
MSG_FILES_ATTACH = "Attaching files to note ... Please wait";
MSG_NOTEBOOKS_REFRESH = "Refreshing the list of notebooks ... Please wait";
MSG_NOTES_LOAD = "Loading a list of notes ... Please wait";
MSG_FAVS_LOAD = "Loading a list of favourite notes ... Please wait";
MSG_QUICKS_LOAD = "Loading a list of Quick Links ... Please wait";
MSG_FAVS_ADD = "Adding to favourites ... Please wait";
MSG_SECTIONS_LOAD = "Loading a list of sections ... Please wait";
MSG_LOAD_NOTE	 = "Loading specified note ... Please wait"
MSG_CONFIG_SAVE = "Saving configuration and starting the application ... Please wait";
ERROR_NOTEBOOKS_LOAD = "Error loading the list of notebooks. Please check logs";
MSG_FAVOURITES_DELETE = "Deleting favourite notes ... Please wait";
MSG_SERVICE_DISABLED = "::service:: service is disabled. Please go to Settings and enable it";
MSG_SERVICE_NOTRELEV = "Not relevant for the service"
MSG_NO_CONTAINERID = "You should select container ID for selected service. For Evernote you should select the notebook, for Onenote - section"
MSG_FAVS_REMOVE = "Removing from favourites ... ";
MSG_NOTE_UPDATE = "Updating the note content ... Please wait"
MSG_TOKEN_UPDATE = "Updating access token"
MSG_TOKEN_UPDATE_OK = "Onenote access token has been successfully updated"
MSG_TOKEN_UPDATE_ERR = "Error while updating access token. Please check server logs"


// HTTP Response codes
HTTP_OK = "200";
HTTP_UNAUTHORIZED = "401";
HTTP_NOT_FOUND = "404"
HTTP_FORBIDDEN = "403"

// Supported MIMEs
mime_pdf = "application/pdf";
mime_doc = "application/msword";
mime_docx = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
mime_xls = "application/vnd.ms-excel";
mime_xls_2 = "application/xls";
mime_xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
mime_ppt = "application/vnd.ms-powerpoint";
mime_pptx = "application/vnd.openxmlformats-officedocument.presentationml.presentation";
mime_jpeg = "image/jpeg";
mime_gif = "image/gif";
mime_png = "image/png"
mime_jpg = "image/jpg"

// Encrypted prefixes and suffixes
encrypted_prefix = "TUFNTU9USEVOQ1JZUFRFRE5PVEU=__"
encrypted_suffix = "__TUFNTU9USEVOQ1JZUFRFRE5PVEU="

function CreateAJAX(url,requestType,dataType,data){
    
    contentType = ""
    switch (requestType)
    {
    	case "GET":
    		contentType = "text/html";
    		break;
    	case "POST":
    		if (dataType == "json"){contentType = "application/json; charset=utf-8";}
    		else{contentType = "application/x-www-form-urlencoded; charset=utf-8";}
    		break;
    }

	return $.ajax({
     	// The URL for the request
    	url: url, 
    	data: data,
    	type: requestType,
    	contentType: contentType,
    	// The type of data we expect back
    	dataType : dataType
	});
}

function scrollTop(){
	$("html, body").animate({ scrollTop: 0 }, "slow");
}
function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function displayProgress(text,display){
	
	if (display){
		$("span#loadingText").html(text);
		$("#modalLoading").modal('show');
	}
	else{
		$("#modalLoading").modal('hide');
	}
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function initModal(modalID){

	$("#"+modalID).modal("show");
	$("#"+modalID).find("h4#modalTitle").html("<img src=\"/static/images/103.gif\"/>");
	$("#"+modalID).find("div#modalContent").html("<img src=\"/static/images/103.gif\"/>");
	$("#"+modalID).find("button#btnApply").hide();
}
function displayModal(modalID, title, content, applyButton){
	$("#"+modalID).find("h4#modalTitle").html(title);
	$("#"+modalID).find("div#modalContent").html(content);
	if (applyButton){$("#"+modalID).find("button#btnApply").show();}
	else{$("#"+modalID).find("button#btnApply").hide();}
}

$(document).on("click","button#btnAlert",function(){
	$(this).parent().hide();
});
$(document).on("click","img#iconHelp",function(){
	$("div#modalHelp").modal('show');
});

function showAlert(display,type,message){
	var alertPanel = $("div#operationResult");
	if (!display){
		alertPanel.hide();
		return;
	}

	// First, clear all alert-success,alert-danger, alert-warning classes
	alertPanel.removeClass("alert-success");
	alertPanel.removeClass("alert-danger");
	alertPanel.removeClass("alert-warning");

	// Setting message
	alertPanel.find("span#alertMessage").html(message);

	// Defining the type of message
	switch (type)
	{
		case LEVEL_WARN:
			alertPanel.addClass("alert-warning");
			break;

		case LEVEL_DANGER:
			alertPanel.addClass("alert-danger");
			break;

		case LEVEL_SUCCESS:
			alertPanel.addClass("alert-success");
			break;

		default:
			alertPanel.addClass("alert-info");
			break;
	}

	// Displaying the panel
	alertPanel.show();

}

function getIcon(mime){
	switch (mime){

		// PDF MIMEs
		case mime_pdf:
			return "icon_pdf.png";

		// Excel MIMEs
		case mime_xls:
		case mime_xls_2:
		case mime_xlsx:
			return "icon_excel.png";

		case mime_doc:
		case mime_docx:
			return "icon_word.png";

		case mime_ppt:
		case mime_pptx:
			return "icon_ppt.png";

		// Image MIMEs
		case mime_gif:
		case mime_jpeg:
		case mime_png:
		case mime_jpg:
			return "icon_image.png"

		// Uknown document
		default:
			return "icon_doc.png";
	}
}


function humanFileSize(bytes, si) {
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1)+' '+units[u];
}

function listFavourites(contentID){

	// Displaying Progress
	displayProgress(MSG_FAVS_LOAD,true);

	CreateAJAX("/favourites/list","GET","html",{format:"list"})
	.done(function(response){
		displayProgress("",false);
		$("div#"+contentID).html(response);
		rows = $("table#tblFavs tr.itemRow");
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(MSG_INTERNAL_ERROR);
	});

}

function remove_from_favourites(type){
	// Displaying modal progress
	displayProgress(MSG_FAVS_REMOVE,true);

	// Sending request
	var favourites = new Array();
	favourites.push($("#txtGuid").val());
	CreateAJAX("/favourites/remove","POST","json",JSON.stringify(favourites)).
	done(function(response){
		displayProgress("",false);
		$("span#favRemove").hide();
		$("span#favAdd").show();
	})
	.fail(function(xhr){
		showToast(LEVEL_DANGER,xhr.responseText);
		displayProgress("",false);
	});
}

function add_to_favourites(guid,title,service){

	// Displaying modal progress
	displayProgress(MSG_FAVS_ADD,true);
	var favourites = new Array();

	// Sending request
	favourites.push({guid:guid,"service":service,"title":title,"updated":"","created":""});
	CreateAJAX("/favourites/add","POST","json",JSON.stringify(favourites)).
	done(function(response){
		displayProgress("",false);
		$("span#favAdd").hide();
		$("span#favRemove").show();
	})
	.fail(function(xhr){
		showToast(LEVEL_DANGER,xhr.responseText);
		displayProgress("",false);
	});
}

function get_note(guid,service,refresh){

    var url = "";
    data = new Array();
    data.push({"refresh":refresh})
	// Displaying progress
	displayProgress(MSG_LOAD_NOTE,true);


	// Generating URL
	switch (service)
	{
		case service_evernote:
			url = "/note/"+guid
			break;
		case service_onenote:
			url = "/note/on/"+guid
			break;
	}

	// Loading note content
	CreateAJAX(url,"POST","json",JSON.stringify({"refresh":refresh}))
	.done(function(response){
		displayProgress("",false);
		if (response.status != HTTP_OK){
			showToast(LEVEL_DANGER,response.message);
			$("div#noteContent").html("n/a");
			$("span#noteTitle").html("n/a");
			return;
		}
		$("span#noteTitle").html(response.message.title);
		if (response.message.content.includes(encrypted_prefix) && response.message.content.includes(encrypted_suffix) ){
			$("div#noteContent").html(show_encrypted_icon(service));
		}
		else{
			$("div#noteContent").html(response.message.content);
		}
		if (response.message.favourite == true){
			$("span#favAdd").hide();
			$("span#favRemove").show();
		}
		else{
			$("span#favAdd").show();
			$("span#favRemove").hide();
		}
	})
	.fail(function(xhr){
		$("div#modalLoading").modal('hide');
		$("span#noteTitle").html("n/a");
		$("div#noteContent").html("Error loading the specified note. Please check logs");
	});

}

function listQuicks(contentID){
	displayProgress(MSG_QUICKS_LOAD,true);
	CreateAJAX("/favourites/quick/list","GET","html",{format:"list"})
	.done(function(response){
		displayProgress("",false);
		$("div#"+contentID).html(response);
		rows = $("table#tblLinks tr.itemRow");
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(MSG_INTERNAL_ERROR);
	});
}


function showToast(type,message){
	toastr.options = {
		"closeButton": false,
		"debug": false,"newestOnTop": false,"progressBar": false,
		"positionClass": "toast-bottom-center","preventDuplicates": false,
		"onclick": null,"showDuration": "300","hideDuration": "1000",
		"timeOut": "6000","extendedTimeOut": "1000","showEasing": "swing",
		"hideEasing": "linear","showMethod": "fadeIn","hideMethod": "fadeOut"
	}

	switch (type)
	{
		case LEVEL_SUCCESS: // success
			toastr['success'](message);
			break;
		case LEVEL_WARN: //warning
			toastr['warning'](message);
			break;
		case LEVEL_DANGER: // error
			toastr['error'](message);
	}
}


// Function used to load a list of Evernote notebooks for droppdown list
function select_notebooks(filter){
	$("div#listNotebooks").html("<img src='/static/images/103.gif'>");
	CreateAJAX("/notebooks/list/select","GET","html",filter)
	.done(function(response){
		$("div#listNotebooks").html(response);
		guid_exists(config.evernote.default_notebook,"txtNotebook");
	})
	.fail(function(xhr){
		$("div#listNotebooks").html(ERROR_NOTEBOOKS_LOAD);
	});
}

// Function used to load a list of Onenote notebooks for dropdown list
function select_onenote_notebooks(filter){
	$("div#listONNotebooks").html("<img src='/static/images/103.gif'/>");
	CreateAJAX("/notebooks/on/list/select","GET","html",filter)
	.done(function(response){
		$("div#listONNotebooks").html(response);
        default_onenote_notebook = config.onenote.default_notebook != "" ? config.onenote.default_notebook  : $("select#txtONNotebook option:selected").val()
        $("select#txtONNotebook").val(default_onenote_notebook);
		// Listing sections for default notebook
		select_sections($("select#txtONNotebook").val(),{});
	})
	.fail(function(xhr){
		$("div#listONNotebooks").html(xhr.responseText);
	});
}

function select_sections(guid,filter){
	$("div#listONSections").html("<img src='/static/images/103.gif'/>");
	if (guid == ""){
		$("div#listONSections").html("<select class='form-control' style='width:50%' id='txtSection'><option value=''>No GUID specified</option></select>");
		return;
	}
	$("div#listONSections").html("<img src='/static/images/103.gif'/>");
	CreateAJAX("/notebooks/on/sections/"+guid+"/select","GET","html",filter)
	.done(function(response){
		$("div#listONSections").html(response);
		guid_exists(config.onenote.default_section,"txtSection");
	})
	.fail(function(xhr){
		console.log(xhr.responseText);
	});
}

function guid_exists(guid,selectElement)
{
	$("select#"+selectElement+" option").each(function(){
		if ($(this).val() == guid){
			$("select#"+selectElement).val(guid);
			return;
		}
	});
}

function parse_json_response(jsonString)
{
	response = jQuery.parseJSON(jsonString);
	return response.message;
}

function clear_array(items)
{
	if (items.length > 0 )
	{
		var newArray = new Array();
		for (i=0;i<items.length;i++){
			if (items[i].name != null){
				newArray.push(items[i]);
			}
		}
		return newArray;
	}
	return items;

}

function replace_all(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function show_encrypted_icon(service){
	switch (service){
		case service_evernote:
			return TPL_PAGE_ENCRYPTED.replace("::icon::","page_encrypted_evernote.png").replace("::pageType::","note");
			break;
		case service_onenote:
			return TPL_PAGE_ENCRYPTED.replace("::icon::","page_encrypted_onenote.png").replace("::pageType::","page");
			break;
	}
}

function update_access_token(token){
	CreateAJAX("/onenote/token/refresh","POST","json",JSON.stringify({refresh:token}))
	.done(function(response){
		showToast(LEVEL_SUCCESS,MSG_TOKEN_UPDATE_OK);
	})
	.fail(function(xhr){
		showToast(LEVEL_DANGER,MSG_TOKEN_UPDATE_ERR);
	});
}

// Loading external scripts
$.getScript('/static/js/init.js',function(){});
$.getScript('/static/js/evernote.js', function(){});
$.getScript('/static/js/onenote.js', function(){});
$.getScript('/static/js/keyevents.js', function(){});

