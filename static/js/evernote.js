$("img#iconEvernote").click(function(){

		// Displaying the modal window
		$("div#modalEvernote").modal('show');
		$("span#loader").show();

		// Sending request
		CreateAJAX("/user","GET","html",{})
		.done(function(response){
			$("span#loader").hide();
			$("div#modalContent").html(response);
		})
		.fail(function(xhr,status){
			$("span#loader").hide();
			$("div#modalContent").html(xhr.responseText);
		})
	});