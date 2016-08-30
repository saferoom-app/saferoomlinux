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