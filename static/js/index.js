$(document).ready(function(){

	$("button#btnCreate").click(function(){
		self.location.href="/create";
	});
	$("button#btnNotebooks").click(function(){
		self.location.href="/list?mode=notebook";
	});
	$("button#btnSearches").click(function(){
		self.location.href="/list?mode=search";
	});
	$("button#btnTags").click(function(){
		self.location.href="/list?mode=tag";
	});
	$("button#btnFavourites").click(function(){
		self.location.href="/favourites";
	});
	$("button#btnSettings").click(function(){
		self.location.href = "/settings";
	});
})


