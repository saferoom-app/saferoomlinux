var rows;
var config;
$(document).ready(function(){
	$("[rel=tooltip]").tooltip({ placement: 'right'});
	$('#summernote').summernote({height:400,
		toolbar:[
			['style', ['bold', 'italic', 'underline', 'clear']],
			['font', ['strikethrough', 'superscript', 'subscript']],
			['fontsize', ['fontsize']],
			['color', ['color']],
			['para', ['ul', 'ol', 'paragraph']],
			['height', ['height']],
			['table', ['table']],
			['help', ['help']]
		]
	});
	// Getting current config
	CreateAJAX("/settings/config","GET","json",{})
	.done(function(response){

		// Setting configured values
		config = response;	
        
        // Checking what service is enabled or disabled
		$("select#txtService").val(config.system.default_service);
		init_notebooks_sections($("select#txtService").val());
		array = config.evernote.default_tags.split(",");
		if (array.length > 0){
			for (i=0;i<array.length;i++){
				$("input#txtTags").tagsinput('add',array[i]);
			}
		}

	})
	.fail(function(xhr){

	});	

	// Regiuster the handler for all buttons
	$("button").on("click",{},buttonHandler);

	// Register the handler for all <selects>
	$("select").on("change",{},selectHandler);
});

function insertFile(file,fileHash){
	var node = document.createElement('p');
	var tpl_attach = "";
	node.setAttribute("id","saferoomAttach");
	switch(file.type)
	{
		case "image/jpeg":
		case "image/gif":
		case "image/png":
			node.innerHTML = TPL_IMAGE_ATTACH.replace("::fileType::",file.type).replace("::filename::",file.name).replace("::filehash::",fileHash).replace("::filename::",file.name).replace("::filename::",file.name);
			break;
		default:
			tpl_attach = replace_all(TPL_ATTACH,"::filename::",file.name);
			tpl_attach = replace_all(tpl_attach,"::filesize::",humanFileSize(file.size,true));
			tpl_attach = replace_all(tpl_attach,"::filehash::",fileHash);
			tpl_attach = replace_all(tpl_attach,"::fileicon::",getIcon(file.type));
			tpl_attach = replace_all(tpl_attach,"::filetype::",file.type);
			node.innerHTML = tpl_attach;			

			break;
	}
	
	$('#summernote').summernote('insertNode', node);
	//$('#summernote').summernote('insertNode',document.createElement("br"))
}

function encrypt_note(mode,password){
    
    var container_id = ""; // Section or Notebook GUID to upload the note to
    var noteContent = ""; // Note content
    var tmpl = ""
    var enml = "";
    var htmlAttach = "";
    var fileList = [];
    var img;
    var note = {}

	showAlert(false,"","");
		// Checking note title
		if ($("input#txtTitle").val() == ""){$("input#txtTitle").focus();return;}

		// Checking container ID
		if (get_container_id(parseInt($("select#txtService").val())) == ""){
			alert(MSG_NO_CONTAINERID);
		}
		
		// Checking note content
		noteContent = $("#summernote").summernote('code');
		if (noteContent == ""){
			alert("Note content cannot be empty");
			return;
		}	

		// Before sending the content to server, let's format it
		tmpl = $("<div>"+noteContent+"</div>");
		tmpl.find("p#saferoomAttach").each(function(){
			// We have image
			if ($(this).html().includes("img class=\"attach\"")){
				img = $(this).find("img");
				fileList.push({name:img.attr("data-filename"),mime:img.attr("data-type"),hash:img.attr("data-hash")});				
			}
			else{
				htmlAttach = $(this).next().html();
				enml = $(this).next().find("span#enml");
				if (enml != null){
					fileList.push({name:$(this).next().find("span#txtFilename").html(),mime:enml.find("en-media").attr("data-type"),hash:enml.find("en-media").attr("data-hash")});
					noteContent = noteContent.replace("<div class=\"attachment\">"+htmlAttach+"</div>",enml.html());
				}
			}
		});
		noteContent = noteContent.replace(/<p><br><\/p>/g, '<br/>');
		fileList = clear_array(fileList);		
		
		// Creating note request
		note['service'] = $("select#txtService").val();
		note['title'] = $("input#txtTitle").val();
		note['tags'] = $("input#txtTags").val();
		switch ($("select#txtService").val()){
			case "0":
				note['notebook_guid'] =$("select#txtNotebook option:selected").val()
				break;
			case "1":
			    note['notebook_guid'] =$("select#txtONNotebook option:selected").val()
			    break;
		}
		note['section_guid'] = $("select#txtSection option:selected").val();
		note['content'] = noteContent;
		note['filelist'] = JSON.stringify(fileList)
		note['mode'] = mode
		note['pass'] = password
		displayProgress(MSG_NOTE_UPLOAD,true);
		CreateAJAX("/note/create","POST","json",note).done(function(response){
			displayProgress("",false);
			if (response.status != HTTP_OK){
				showAlert(true,LEVEL_DANGER,response.message);
				scrollTop();
				return;
			}
			showAlert(true,LEVEL_SUCCESS,response.message);
			scrollTop();
		})
		.fail(function(xhr){
			displayProgress("",false);
			showAlert(true,LEVEL_DANGER,MSG_INTERNAL_ERROR);
		});s
}

function init_notebooks_sections(selected_service){
	$("div[id*='Notebooks']").hide();
	switch(true){
		case (parseInt(selected_service) === service_evernote): // Evernote
			// Disabling sections
			$("div#listONSections").html(tpl_select_disabled.replace("::id::","txtSection").replace("::message::",MSG_SERVICE_NOTRELEV));
			$("div#listNotebooks").show();
			if (config.evernote.status == true){
				select_notebooks({});
			}
			else{
				showToast(LEVEL_WARN,MSG_SERVICE_DISABLED.replace("::service::","Evernote"));
				$("div#listNotebooks").html(tpl_select_disabled.replace("::id::","txtNotebook").replace("::message::",MSG_SERVICE_DISABLED.replace("::service::","Evernote")));
			}
			break;

		case (parseInt(selected_service) === service_onenote):
			$("div#listONNotebooks").show();
			if (config.onenote.status == true){
				select_onenote_notebooks({});
			}
			else{
				$("div#listONNotebooks").html(tpl_select_disabled.replace("::id::","txtONNotebook").replace("::message::",MSG_SERVICE_DISABLED.replace("::service::","Onenote")));
				$("div#listONSections").html(tpl_select_disabled.replace("::id::","txtONNotebook").replace("::message::",MSG_SERVICE_DISABLED.replace("::service::","Onenote")));
					showToast(LEVEL_WARN,MSG_SERVICE_DISABLED.replace("::service::","Onenote"));
			}
			break;

	}
}

function get_container_id(service){
	container_id = ""
	switch (service)
	{
		case service_evernote:
			container_id = $("select#txtNotebook option:selected").val();
			break;
		case service_onenote:
			container_id = $("select#txtSection option:selected").val();
			break;
	}
	if (container_id == null){
		return "";
	}
	return container_id;
}


// Handlers
function buttonHandler(event){
	var id = event.currentTarget.id
	switch (id)
	{
		// OTP Encrypt button handler
		case "btnOTPEncrypt":
			$("input#txtOTP").val("");
			$("div#modalOTP").modal("show");
			break;

		// Button "Apply" in "Encrypt OTP" dialog
		case "btnOTPApply":
			// Checking if the password has been specified
			if ($("input#txtOTP").val() == ""){
				$("input#txtOTP").focus();
				return;
			}

			// Closing modal window and start decryption procedure
			$("div#modalOTP").modal("hide");
			encrypt_note("otp",$("input#txtOTP").val());
			break;

		case "btnAttach":
			$("input#txtFiles").focus().trigger("click");
			break;

		case "btnClear":
			$("#summernote").summernote('reset');
			break;

		case "btnEncrypt":
			encrypt_note("master","");
			break;

		case "btnRefresh":
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
			});
			break;

		case "btnApply":
			tagList = new Array();
			$("table#tblTags tr").each(function(){
				if ($(this).find("input").prop("checked") == true){
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
			break;

		case "btnTags":
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
			});
			break;
	}
}

function selectHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "txtService":
			init_notebooks_sections($("option:selected",this).val(),config.system);
			break;
	}
}

$(document).on("keyup","input#txtSearch",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	rows.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});

$(document).on("click","input#chkAll",function(){
	$('input:checkbox').not(this).prop('checked', this.checked);
});
$(document).on("change","input#txtFiles",function(){
	selectedFiles = $(this)[0].files;
	if (selectedFiles.length == 0){return;}
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
	select_notebooks({refresh:"True"});
});
$(document).on("click","button#btnRefreshONNotebooks",function(){
	select_onenote_notebooks({refresh:"True"});
});
