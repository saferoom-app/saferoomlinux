var tree;
var onRows;
var sectionGUID = "";
var notebookGUID = "";
$(document).ready(function(){
	getJSON();	
});

function getJSON()
{
	displayProgress(MSG_NOTEBOOKS_LOAD,true);
	CreateAJAX("/notebooks/on/list/json","GET","json",[])
	.done(function(response){
		displayProgress("",false);
		// Checking the response
		if (response.status != HTTP_OK ){
			showToast(LEVEL_DANGER,response.message);
		}
		tree = response.message;
		$('div#tree').treeview({data: tree});
		$('div#tree').on('nodeSelected', function(event, data) {
			data.selected = true;
  			listItems(data);
		});

		notebookGUID = getParameterByName("notebook",document.location.href);
		if (notebookGUID !=null){
			setTimeout(function(){
				listSections("/on/sections/"+notebookGUID+"/json");
			},500);
		};
		sectionGUID = getParameterByName("section",document.location.href);
		if (sectionGUID !=null){
			var interval = window.setInterval(function(){
			if (FINISHED){
				listONNotes("/on/list/"+sectionGUID+"/list");
				clearInterval(interval);
			}
			},500);
		};
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(MSG_INTERNAL_ERROR);
	});
}

function listSections(href){

	// Getting notebook GUID
	array = href.split("/");
	notebookGUID = array[array.length-2]
	displayProgress(MSG_SECTIONS_LOAD,true);
	CreateAJAX("/notebooks"+href,"GET","json",{})
	.done(function(response){
        displayProgress("",false);
		if (response.status != HTTP_OK){
			showToast(LEVEL_DANGER,response.message);
			return;
		}
		appendNodes(response.message,href);		
		$('div#tree').treeview({data: tree});
		$('div#tree').on('nodeSelected', function(event, data) {
			data.selected = true;
  			listItems(data);
		});
		FINISHED = true;		
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(xhr.responseText);
	});
}

function listItems(data){
	if (data.href.includes("sections")){
		sectionGUID = "";
		listSections(data.href);
	}
	else if (data.href.includes("list")){
		listONNotes(data.href,false);
	}
}

function appendNodes(object,href)
{
	// Getting GUID from HREF
	array = href.split("/")
	guid = array[array.length-2];
	for (i=0;i<tree.length;i++){
		if (tree[i].href.includes(guid)){
			tree[i].nodes = object;		
		}
	}	
}

function listONNotes(href,forceRefresh){
	array = href.split("/")
	sectionGUID = array[array.length-2];
	displayProgress(MSG_NOTES_LOAD,true);
	CreateAJAX("/note"+href,"GET","html",{"refresh":forceRefresh})
	.done(function(response){
		displayProgress("",false);
		$("div#listNotes").html(response);
		onRows = $("table#tblNotes tr.itemRow");
		FINISHED = true;
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listNotes").html(xhr.responseText);
	});
}
$(document).on("keyup","input#txtONSearch",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	onRows.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});
$(document).on("click","button#btnNoteRefresh",function(){
	listONNotes("/on/list/"+sectionGUID+"/list",true);
});
$(document).ajaxComplete(function(){
	path = {"notebook":notebookGUID,"section":sectionGUID};
});



