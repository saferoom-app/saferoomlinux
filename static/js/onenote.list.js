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

	CreateAJAX("/notebooks"+href,"GET","json",{})
	.done(function(response){
		$('div#tree').treeview({data: tree});
		$('div#tree').on('nodeSelected', function(event, data) {
  			listItems(data);
		});
	})
	.fail(function(xhr){

	});

}

function listItems(data)
{
	if (data.href.includes("sections")){
		listSections(data.href);
	}
	else if (data.href.includes("notes")){
		listNotes(data.href);
	}
}



