$(document).ready(function(){

	$("button#btnCreate").click(function(){
		self.location.href="/create";
	});
	$("li#linkEvernote").click(function(){
		self.location.href="/list?mode=notebook";
	});
	$("li#linkOnenote").click(function(){
		self.location.href="/on/list?mode=notebook";
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


