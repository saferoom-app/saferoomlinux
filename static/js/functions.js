/*
	Global variables section
*/

var FINISHED = false;

TPL_ATTACH = "<div class=\"attachment\"><div class=\"row\"><div class=\"col-md-10\" style=\"display:inline-block\"><span style=\"margin-left:10px\"><img src=\"/static/images/::fileicon::\"/></span><span style=\"margin-left:10px\"><a href=\"/tmp/::filename::\">::filename:: (Size: ::filesize::)</a></span><span id='enml'><en-media type=\"::fileType::\" hash=\"::fileHash::\" /></span></div><div class=\"col-md-2\"><span id='txtFilename' style='display:none'>::filename::</span><span class=\"pull-right\" style=\"margin-right:10px\"><span id='removeAttach' class=\"glyphicon glyphicon-remove link\" aria-hidden=\"true\"></span></span></div></div></div><br/>";

TPL_IMAGE_ATTACH = "<img width=\"100%\" src=\"/static/tmp/::filename::\"/><span id='enml'><en-media type=\"::fileType::\" hash=\"::fileHash::\" /></span><span style=\"display:none\" id='txtFilename'>::filename::</span>";

// Type of alerts
LEVEL_INFO = 0;
LEVEL_SUCCESS = 1;
LEVEL_WARN = 2;
LEVEL_DANGER = 3;

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
ERROR_NOTEBOOKS_LOAD = "Error loading the list of notebooks. Please check logs";

// HTTP Response codes
HTTP_OK = "200";
HTTP_UNAUTHORIZED = "401";
HTTP_NOT_FOUND = "404"
HTTP_FORBIDDEN = "403"

// Path object to generate links
path = new Array();


function CreateAJAX(url,requestType,dataType,data){
	return $.ajax({
     	// The URL for the request
    	url: url, 
    	data: data,
    	type: requestType,
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
		case "application/pdf":
			return "icon_pdf.png";

		// Excel MIMEs
		case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
		case "application/vnd.ms-excel":
		case "application/xls":
			return "icon_excel.png";

		case "application/msword":
		case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
			return "icon_word.png";

		case "application/vnd.ms-powerpoint":
		case "application/vnd.openxmlformats-officedocument.presentationml.presentation":
			return "icon_ppt.png";

		// Image MIMEs
		case "image/gif":
		case "image/jpeg":
		case "image/png":
		case "image/jpg":
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
		$("div#listONNotebooks").html(response);
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


// Loading external scripts
$.getScript('/static/js/evernote.js', function(){});
$.getScript('/static/js/onenote.js', function(){});
$.getScript('/static/js/keyevents.js', function(){});