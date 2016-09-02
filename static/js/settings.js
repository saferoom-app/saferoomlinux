$(document).ready(function(){
	$("[rel=tooltip]").tooltip({ placement: 'right'});

	// Loading the cache information
	CreateAJAX("/settings/cache","GET","json",{})
	.done(function(response){
		console.log(response);
		for (var key in response){
			$("td#cache_"+key).html(response[key]);
		}
	})
	.fail(function(xhr){

	});	

});