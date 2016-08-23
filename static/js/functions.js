/*
	Global variables section
*/

var FINISHED = false;

TPL_ATTACH = "<div class=\"attachment\"><div class=\"row\"><div class=\"col-md-10\" style=\"display:inline-block\"><span style=\"margin-left:10px\"><img src=\"/static/images/::fileicon::\"/></span><span style=\"margin-left:10px\"><a href=\"/tmp/::filename::\">::filename:: (Size: ::filesize::)</a></span><span id='enml'><en-media type=\"::fileType::\" hash=\"::fileHash::\" /></span></div><div class=\"col-md-2\"><span id='txtFilename' style='display:none'>::filename::</span><span class=\"pull-right\" style=\"margin-right:10px\"><span id='removeAttach' class=\"glyphicon glyphicon-remove link\" aria-hidden=\"true\"></span></span></div></div></div><br/>";

TPL_IMAGE_ATTACH = "<img src=\"/static/tmp/::filename::\"/><span id='enml'><en-media type=\"::fileType::\" hash=\"::fileHash::\" /></span><span id='txtFilename'>::filename::</span>";

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
ERROR_NOTEBOOKS_LOAD = "Error loading the list of notebooks. Please check logs";

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


function listNotes(filter){
	
	// Displaying modal window
	displayProgress(MSG_NOTES_LOAD,true)

	CreateAJAX("/note/list","POST","html",filter)
	.done(function(response){
		displayProgress("",false);
		$("div#listNotes").html(response);
		rows = $("table#tblNotes tr");
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listNotes").html(xhr.responseText);
	});

}

function listNotebooks(){
	// Displaying modal window
	displayProgress(MSG_NOTEBOOKS_LOAD,true)
	
	CreateAJAX("/notebooks/list/html","GET","html",{})
	.done(function(response){
		displayProgress("",false);
		$("div#listItems").html(response);
		rowItems = $("div#listNotebooks button");
		FINISHED = true;
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listItems").html(response);
		FINISHED = true;
	});

}

function listTags(filter){
	// Displaying modal window
	displayProgress(MSG_TAGS_LOAD, true);
	CreateAJAX("/tags/list","GET","html",filter)
	.done(function(response){
		displayProgress("",false);
		$("div#listItems").html(response);
		rowItems = $("div#listTags button");
		FINISHED = true;
	})
	.fail(function(xhr){
		FINISHED = true;
		displayProgress("",false);
		$("div#listItems").html(response);
	});
}

function listSearches(){

	// Displaying modal window
	displayProgress(MSG_SEARCHES_LOAD,true);

	CreateAJAX("/searches/list/html","GET","html",{})
	.done(function(response){
		displayProgress("",false);
		$("div#listItems").html(response);
		rowItems = $("div#listSearches button");
		FINISHED = true;
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listItems").html(response);
		FINISHED = true;
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

// Loading external scripts
$.getScript('/static/js/evernote.js', function(){});
$.getScript('/static/js/keyevents.js', function(){});