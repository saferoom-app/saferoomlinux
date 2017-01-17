$("img#iconOnenote").click(function(){
	//window.open("/onenote/login","_blank","width:600px;height:400px");
	// Displaying the modal window
		$("div#modalOnenote").modal('show');
		$("span#loader").show();
		$("div#modalContent").html("");
		// Sending request
		CreateAJAX("/onenote/user","GET","html",{})
		.done(function(response){
			$("span#loader").hide();
			$("div#modalContent").html(response);
		})
		.fail(function(xhr,status){
			$("span#loader").hide();
			$("div#modalContent").html(xhr.responseText);
		})
});

$(document).on("click","button#btnTokenRefresh",function(){
	window.open("/onenote/token/refresh","_blank","width=600,height=400");
});
$(document).on("click","button#btnLogin",function(){
	window.open("/onenote/login","_blank","width=600,height=400");
});