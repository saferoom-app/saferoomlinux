var rows;
$(document).ready(function(){
	// List all the Favourite notes
	listFavourites("favs");

	$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  		switch($(e.target).prop("id"))
  		{
  			case "tabFavs":
  				listFavourites("favs");
  				break;
  			case "tabQuicks":
  				listQuicks("quicks");
  				break;
  		}
  	});
});

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