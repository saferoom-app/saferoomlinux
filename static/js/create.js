var rows;
$(document).ready(function(){
	$('#summernote').summernote({height:300});

	$.getScript('/static/js/evernote.js', function(){});

	// Loading a list of notebooks
	CreateAJAX("/notebooks/list/select","GET","html",{})
	.done(function(response){
		$("div#listNotebooks").html(response);
	})
	.fail(function(xhr){
		$("div#listNotebooks").html(ERROR_NOTEBOOKS_LOAD);
	});

	$("button#btnAttach").click(function(){
		$("input#txtFiles").focus().trigger("click");
		//insertFile();
	});

	$("button#btnClear").click(function(){
		$("#summernote").summernote('reset');
	});

	$("button#btnEncrypt").click(function(){

		showAlert(false,"","");
		// Checking note title
		var title = $("input#txtTitle").val();
		if (title == ""){$("input#txtTitle").focus();return;}

		// Checking note content
		var noteContent = $("#summernote").summernote('code');
		if (noteContent == ""){
			noteContent.focus();
			alert("Note content cannot be empty");
			return;
		}

		// Setting tags
		var tags = $("input#txtTags").val();

		// Setting notebook GUID
		var guid = $("select#txtNotebook option:selected").val();

		// Before sending the content to server, let's format it
		var tmpl = $("<div>"+noteContent+"</div>");
		var enml = "";
		var htmlAttach = "";
		var fileList = []
		tmpl.find("p#evernoteAttach").each(function(){
			htmlAttach = $(this).next().html();
			enml = $(this).next().find("span#enml");
			if (enml != null){
				fileList.push({name:$(this).next().find("span#txtFilename").html(),mime:enml.find("en-media").attr("type")});
				noteContent = noteContent.replace("<div class=\"attachment\">"+htmlAttach+"</div>",enml.html());
			}
		});
		noteContent = noteContent.replace(/<p><br><\/p>/g, '<br/>');
		displayProgress(MSG_NOTE_UPLOAD,true);
		CreateAJAX("/note/create","POST","json",{title:title,content:noteContent,tags:tags,guid:guid,filelist:JSON.stringify(fileList)})
		.done(function(response){
			displayProgress("",false);
			showAlert(true,LEVEL_SUCCESS,response.msg);
			scrollTop();
		})
		.fail(function(xhr){
			displayProgress("",false);
			showAlert(true,LEVEL_DANGER,MSG_INTERNAL_ERROR);
		});

	});	

});

$(document).on("change","input#txtFiles",function(){
	selectedFiles = $(this)[0].files;
	if (selectedFiles.length == 0){
		return;
	}
	var fd = new FormData();
	// Processing the list of files
	for (i=0;i<selectedFiles.length;i++){
		fd.append("attach[]",selectedFiles[i]);
	}
	
	// We need upload these files to temporary folder
	displayProgress(MSG_FILES_ATTACH,true);
	$.ajax({url : '/upload',type : 'POST',data : fd,
       processData: false,  // tell jQuery not to process the data
       contentType: false  // tell jQuery not to set contentType
	})
	.done(function(response){
		displayProgress("",false);
		for (i=0;i<selectedFiles.length;i++){
			insertFile(selectedFiles[i],response[i])
		}
	})
	.fail(function(xhr){
		displayProgress("",false);
		alert(MSG_INTERNAL_ERROR);
	})
});

$(document).on("click","span#removeAttach",function(){
	$(this).parent().parent().parent().parent().remove();
});
$(document).on("click","button#btnRefreshNotebooks",function(){

	// Displaying progress
	displayProgress(MSG_NOTEBOOKS_REFRESH,true);

	CreateAJAX("/notebooks/list/select","GET","html",{refresh:"True"})
	.done(function(response){
		displayProgress("",false);
		$("div#listNotebooks").html(response);
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("div#listNotebooks").html(ERROR_NOTEBOOKS_LOAD);
	});

});


function insertFile(file,fileHash){
	var node = document.createElement('p');
	node.setAttribute("id","evernoteAttach");
	switch(file.type)
	{
		case "image/jpeg":
		case "image/gif":
		case "image/png":
			node.innerHTML = TPL_IMAGE_ATTACH.replace("::filename::",file.name).replace("::filename::",file.name).replace("::fileType::",file.type).replace("::fileHash::",fileHash);
			break;
		default:
			node.innerHTML = TPL_ATTACH.replace("::filename::",file.name).replace("::filename::",file.name).replace("::filename::",file.name).replace("::fileicon::",getIcon(file.type)).replace("::filesize::",file.size).replace("::fileType::",file.type).replace("::fileHash::",fileHash);
			break;
	}
	
	$('#summernote').summernote('insertNode', node);
	//$('#summernote').summernote('insertNode',document.createElement("br"))

}



$(document).on("click","button#btnTags",function(){

	$("div#modalTags").modal('show');

	// Loading a list of tags
	CreateAJAX("/tags/list/","GET","html",{format:"select",refresh:"False"})
	.done(function(response){
		$("span#loader").hide();
		$("div#listTags").html(response);
		rows = $("table#tblTags tr");
	})
	.fail(function(xhr){
		$("span#loader").hide();
		$("div#listTags").html(xhr.responseText);
	})
});
$(document).on("keyup","input#txtSearch",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	rows.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});
$(document).on("click","button#btnRefresh",function(){
	// Loading a list of tags
	$("span#loader").show();
	CreateAJAX("/tags/list/","GET","html",{format:"select",refresh:"True"})
	.done(function(response){
		$("span#loader").hide();
		$("div#listTags").html(response);
		rows = $("table#tblTags tr");
	})
	.fail(function(xhr){
		$("span#loader").hide();
		$("div#listTags").html(xhr.responseText);
	})
})

$(document).on("click","input#chkAll",function(){
	$('input:checkbox').not(this).prop('checked', this.checked);
});

$(document).on("click","button#btnApply",function(){
	tagList = new Array();
	$("table#tblTags tr").each(function(){
		if ($(this).find("input").prop("checked") == true)
		{
			if ($(this).find("span").length != 0){
				tagList.push($(this).find("span").html());
			}
		}
	});

	for (i=0;i<tagList.length;i++){
		$("input#txtTags").tagsinput('add',tagList[i]);
	}
	$("div#modalTags").modal("hide");
	$("div#listTags").html("");
});