var elem = null;
$(document).ready(function(){

	// Getting note GUID
	GUID = $("input#txtGuid").val();
	
	// Getting note
	get_note(GUID,service_evernote,false);	

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
			add_to_favourites($("#txtGuid").val(),$("span#noteTitle").html(),service_evernote);
			break;
		case "btnRemFav":
			remove_from_favourites("json");
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

		case "btnUpdate":
			update_note(guid,service);
			break;
	}
}