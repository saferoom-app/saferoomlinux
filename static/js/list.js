var rows = "";
var rowItems;
var selectedGUID = "";
var currentMode = "notebook"
var guid = ""
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
				listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False"});
				clearInterval(interval);
			}
		},500);
	}
});

$(document).on("click","div#listNotebooks button",function(){
	selectedGUID = $(this).attr("id");
	currentMode = "notebook"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False"});
	scrollTop();
});

$(document).on("click","div#listTags button",function(){
	selectedGUID = $(this).attr("id");
	currentMode = "tag"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False"});
	scrollTop();
});

$(document).on("click","div#listSearches button",function(){
	selectedGUID = $(this).find("input#query").val();
	currentMode = "search"
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"False"});
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
$(document).on("click","button#btnRefresh",function(){
	listNotes({type:currentMode,guid:selectedGUID,format:"html","refresh":"True"});
});

$(document).on("change","select#selectCategory",function(){
	listCategories($("option:selected",this).val());
});
$(document).ajaxComplete(function(){
	path = {"mode":currentMode,"guid":selectedGUID};
});




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
		$("div#listItems").html(xhr.responseText);
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