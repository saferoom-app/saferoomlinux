var elem = null;
$(document).ready(function(){

	// Getting note GUID
	GUID = $("input#txtGuid").val();
	// Displaying modal window
	displayProgress(MSG_LOAD_NOTE,true);
	
	// Loading note content
	CreateAJAX("/note/"+GUID,"POST","json",{})
	.done(function(response){
		displayProgress("",false);
		if (response.status != HTTP_OK){
			showToast(LEVEL_DANGER,response.message);
			$("div#noteContent").html("n/a");
			$("span#noteTitle").html("n/a");
			return;
		}
		$("span#noteTitle").html(response.message.title);
		if (response.message.content.includes(encrypted_prefix) && response.message.content.includes(encrypted_suffix) ){
			$("div#noteContent").html(show_encrypted_icon(service_evernote));
		}
		else{
			$("div#noteContent").html(response.message.content);
		}
		if (response.message.favourite == true){
			$("span#favAdd").hide();
			$("span#favRemove").show();
		}
		else{
			$("span#favAdd").show();
			$("span#favRemove").hide();
		}
	})
	.fail(function(xhr){
		$("div#modalLoading").modal('hide');
		$("span#noteTitle").html("n/a");
		$("div#noteContent").html("Error loading the specified note. Please check logs");
	});

	// Register global button handler
	$("button").on("click",{},buttonHandler);
});

function decrypt_note(mode,password){
	// Displaying progress
	$("div#decryptedContent").html("")
	$("#modalDecrypted").modal("show");
	$("div#modalDecrypted span#loader").show();

	CreateAJAX("/note/decrypt","POST","html",{guid:$("#txtGuid").val(),mode:mode,"pass":password})
	.done(function(response){
		$("div#modalDecrypted span#loader").hide();
		$("div#decryptedContent").html(response);
	})
	.fail(function(xhr){
		$("div#modalDecrypted span#loader").hide();
		$("div#decryptedContent").html(xhr.responseText);
	});
}

function buttonHandler(event){
	var id = event.currentTarget.id
	switch (id){
		case "btnAddFav":
			// Displaying modal progress
			displayProgress(MSG_FAVS_ADD,true);
			// Sending request
			item = {guid:$("#txtGuid").val(),"service":0,"title":$("span#noteTitle").html(),"updated":"","created":""};
			CreateAJAX("/favourites/add","POST","json",item).
			done(function(response){
				displayProgress("",false);
				$("span#favAdd").hide();
				$("span#favRemove").show();
			})
			.fail(function(xhr){
				showToast(LEVEL_DANGER,xhr.responseText);
				displayProgress("",false);				
			});
			break;
		case "btnRemFav":
			// Displaying modal progress
			displayProgress(MSG_FAVS_REMOVE,true);

			// Sending request
			favourites = new Array();
			favourites.push($("#txtGuid").val());
			CreateAJAX("/favourites/remove","POST","json",{"delete":JSON.stringify(favourites)}).	done(function(response){
				displayProgress("",false);
				$("span#favRemove").hide();
				$("span#favAdd").show();
			})
			.fail(function(xhr){
				showToast(LEVEL_DANGER,xhr.responseText);
				displayProgress("",false);
			});
			break;
		case "btnOTPApply":
			elem = $("input#txtOTP");
			// Checking if the password has been specified
			if (elem.val() == ""){elem.focus();return;}
			// Closing modal window and start decryption procedure
			$("div#modalOTP").modal("hide");
			decrypt_note("otp",elem.val());
			break;
		case "btnOTPDecrypt":
			$("input#txtOTP").val("");
			$("div#modalOTP").modal("show");
			break;
		case "btnDecrypt":
			decrypt_note("master","");
			break;
	}
}