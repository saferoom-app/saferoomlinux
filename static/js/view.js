var elem = null;
$(document).ready(function(){

	// Getting note GUID
	GUID = $("input#txtGuid").val();
	
	// Getting note
	get_note(GUID,service_evernote,false);	

	// Register global button handler
	$("button").on("click",{},buttonHandler);

	// Make all buttons invisible
	$("button[id*=crypt]").hide();

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
			if ($("input#otpMode").val() == "encrypt"){
				encrypt_notes([GUID],service_evernote,"otp",elem.val());
			}
			else{decrypt_note("otp",elem.val());}
			break;
		case "btnOTPDecrypt":
			$("input#txtOTP").val("");
			$("input#otpMode").val("decrypt");
			$("div#modalOTP").modal("show");
			break;

		case "btnDecrypt":
			decrypt_note("master","");
			break;

		case "btnUpdate":
			get_note(GUID,service_evernote,true);
			break;

		case "btnEncrypt":
			encrypt_notes([GUID],service_evernote,"master","");
			break;

		case "btnOTPEncrypt":
			$("input#txtOTP").val("");
			$("input#otpMode").val("encrypt");
			$("div#modalOTP").modal("show");
			break;
	}
}

function show_buttons(is_encrypted){

	// First, hide all buttons
	$("button[id*=crypt]").hide();

	// Display encrypt buttoms
	if (is_encrypted){$("button[id*=Decrypt]").css('margin-left','10px').show();}
	else{$("button[id*=Encrypt]").css('margin-left','10px').show();}
}

$(document).on("click","li a",function(){
	switch (this.id){
		case "backup_restore":
			restore_from_backup(GUID,service_evernote);
			break;
		case "backup_view":
			view_backup(GUID,service_evernote);
			break;
		case "backup_delete":
			delete_backup(GUID);
			break;
	}
})