var rows = "";
var rowItems;
var selectedGUID = "";
var currentMode = "notebooks"
var guid = ""
var display = notes_all;
var guids = new Array();

// ===========================================
//  	Document events
// ===========================================

$(document).ready(function(){

	// Checking GET parameters: 
	// mode = defines the current category: notebook, tag, search
	// guid = defines the selected object's GUID: notebook, tag or search
	mode = getParameterByName("mode",document.location.href);
	if (mode != null){currentMode = mode;}
	$("select#selectCategory").val(currentMode)
	listCategories(currentMode);

	// Checking guid
	guid = getParameterByName("guid",document.location.href);
	if (guid != null){
		selectedGUID = guid
		var interval = window.setInterval(function(){
			if (FINISHED){
				listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False",display:display});
				clearInterval(interval);
			}
		},500);
	}
});
$(document).on("click","div#listNotebooks button",function(){
	selectedGUID = $(this).attr("id");
	currentMode = "notebook"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False",display:display});
	scrollTop();
});
$(document).on("click","div#listTags button",function(){
	selectedGUID = $(this).attr("id");
	currentMode = "tag"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False",display:display});
	scrollTop();
});
$(document).on("click","div#listSearches button",function(){
	selectedGUID = $(this).find("input#query").val();
	currentMode = "search"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False",display:display});
	scrollTop();
});
$(document).on("keyup","input#txtSearch",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	rows.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});
$(document).on("keyup","input#txtFilter",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	rowItems.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});
$(document).on("change","select#selectCategory",function(){
	listCategories($("option:selected",this).val());
});
$(document).ajaxComplete(function(){
	path = {"mode":currentMode,"guid":selectedGUID};
});
$(document).on("click","li a",function(){
	var id = this.id;
	$("ul.dropdown-menu li").find("i").hide();
	$("li a#"+id).find("i").show();
	switch (id){
		case "show_all":
			display = notes_all;
			break;
		case "show_enc":
			display = notes_encrypted_only;
			break;
		case "show_plain":
			display = notes_plain_only;
			break;
	}
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"True",display:display});
})

$(document).on("click","button",buttonHandler);
$(document).on("click","#selectAll",function(){
	$("input[type=checkbox]").prop('checked',$(this).is(":checked"));
});

// ===========================================
//  	Functions and Handlers
// ===========================================

function listCategories(category){
	switch (category){
		case "tag":
			listTags({});
			break;
		case "search":
			listSearches();
			break;
		default: // notebooks
			listNotebooks();
			break;
	}
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
		$("div#listItems").html(xhr.responseText);
		FINISHED = true;
	});}

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
		$("div#listItems").html(xhr.responseText);
	});}

function listNotes(filter){
	
	// Displaying modal window
	display_inline_progress("note_list");

	CreateAJAX("/note/list","POST","html",filter)
	.done(function(response){
		$("div#listNotes").html(response);
		rows = $("table#tblNotes tr");
		set_display_options();
	})
	.fail(function(xhr){
		$("div#listNotes").html(xhr.responseText);
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
		$("div#listItems").html(xhr.responseText);
		FINISHED = true;
	});
}
function set_display_options(){
	switch (display){
		
		case notes_plain_only:
			$("li a#show_plain").find("i").show();
			break;
		case notes_encrypted_only:
			$("li a#show_enc").find("i").show();
			break;
		default:
			$("li a#show_all").find("i").show();
			break;
	}
}

function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "btnRefresh":
			listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"True",display:display});
			break;
		case "btnEncrypt":
			// Checking that at least one note is selected
			check_selected_notes();
			encrypt_notes(guids,service_evernote,"master","");
			break;
		case "btnOTPEncrypt":
			check_selected_notes();
			$("input#txtOTP").val("");
			$("div#modalOTP").modal("show");
			break;
		case "btnOTPApply":
			elem = $("input#txtOTP");
			// Checking if the password has been specified
			if (elem.val() == ""){elem.focus();return;}
			// Closing modal window and start decryption procedure
			$("div#modalOTP").modal("hide");
			encrypt_notes(guids,service_evernote,"otp",elem.val());
			break;
	}

}

function check_selected_notes(){
    guids = [];var chkBox;
	$("table#tblNotes tr.itemRow").each(function(){
		chkBox = $(this).find("input[type=checkbox]");
		if (chkBox.is(":checked")){guids.push(chkBox.prop("id"));}
	});
	if (guids.length == 0){alert(ERROR_NO_NOTES);return false;}
}

