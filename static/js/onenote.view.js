$(document).ready(function(){

	// Getting note GUID
	GUID = $("input#txtGuid").val();
	// Displaying modal window
	displayProgress(MSG_LOAD_NOTE,true);
	// Loading note content
	CreateAJAX("/note/on/"+GUID,"POST","json",{})
	.done(function(response){
		$("span#noteTitle").html(response.title);
		$("div#noteContent").html(response.content);
		console.log(response.content);
		displayProgress("",false);
		/*if (response.favourite == true){
			$("span#favAdd").hide();
			$("span#favRemove").show();
		}
		else{
			$("span#favAdd").show();
			$("span#favRemove").hide();
		}*/
	})
	.fail(function(xhr){
		displayProgress("",false);
		$("span#noteTitle").html("n/a");
		$("div#noteContent").html("Error loading the specified note. Please check logs");
	});

});

$(document).on("click","button#btnDecrypt",function(){

	// Displaying progress
	$("div#decryptedContent").html("")
	$("#modalDecrypted").modal("show");
	$("div#modalDecrypted span#loader").show();

	CreateAJAX("/note/decrypt","POST","html",{guid:$("#txtGuid").val()})
	.done(function(response){
		$("div#modalDecrypted span#loader").hide();
		$("div#decryptedContent").html(response);
	})
	.fail(function(xhr){
		$("div#modalDecrypted span#loader").hide();
		$("div#decryptedContent").html(xhr.responseText);
	});
});

$(document).on("click","button#btnAddFav",function(){

	// Displaying modal progress
	displayProgress(MSG_FAVS_ADD,true)

	// Sending request
	item = {guid:$("#txtGuid").val(),"service":0,"title":$("span#noteTitle").html(),"updated":"","created":""}
	CreateAJAX("/favourites/add","POST","json",item).
	done(function(response){
		displayProgress("",false);
		$("span#favAdd").hide();
		$("span#favRemove").show();
	})
	.fail(function(xhr){
		displayProgress("",false);
		console.log(xhr);
	});
});

$(document).on("click","button#btnRemFav",function(){
	// Displaying modal progress
	displayProgress("Removing from favourites ... ",true)

	// Sending request
	item = {guid:$("#txtGuid").val()}
	CreateAJAX("/favourites/remove","POST","json",item).
	done(function(response){
		displayProgress("",false);
		$("span#favRemove").hide();
		$("span#favAdd").show();
	})
	.fail(function(xhr){
		displayProgress("",false);
		console.log(xhr);
	});
});