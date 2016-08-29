var tree;
$(document).ready(function(){
	getJSON();
});

function getJSON()
{
	displayProgress(MSG_NOTEBOOKS_LOAD,true);
	CreateAJAX("/notebooks/on/list/json","GET","json",[])
	.done(function(response){
		displayProgress("",false);
		tree = response
		$('div#tree').treeview({data: tree});
		$('div#tree').on('nodeSelected', function(event, data) {
  			listItems(data);
		});
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(MSG_INTERNAL_ERROR);
	});
}

function listSections(href){
	displayProgress(MSG_SECTIONS_LOAD,true);
	CreateAJAX("/notebooks"+href,"GET","json",{})
	.done(function(response){
		appendNodes(response,href);
		displayProgress("",false);
		$('div#tree').treeview({data: tree});
		$('div#tree').on('nodeSelected', function(event, data) {
  			listItems(data);
		});
	})
	.fail(function(xhr){
		displayProgress("",false);
	});
}

function listItems(data){
	if (data.href.includes("sections")){
		listSections(data.href);
	}
	else if (data.href.includes("list")){
		listONNotes(data.href);
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

function listONNotes(href){
	displayProgress(MSG_NOTES_LOAD,true);
	CreateAJAX("/note"+href,"GET","json",{})
	.done(function(response){
		displayProgress("",false);
		$("div#listNotes").html(response);
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listNotes").html(xhr.responseText);
	});
}



