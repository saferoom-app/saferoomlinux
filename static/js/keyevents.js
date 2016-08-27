linkRows = ""
link = ""
$(document).bind('keydown', function(event) { 
    if (event.which == 81 && event.ctrlKey){
        event.preventDefault();
        initModal("modalQuick");
        CreateAJAX("/favourites/quick/add","GET","html",{})
        .done(function(response){
            displayModal("modalQuick","Add to Quick Links",response,true);
            $("div#modalQuick").find("input#txtquickLink")
                .val(generateLink(path));
        })
        .fail(function(xhr){
            displayModal("modalQuick","Add to Quick Links",xhr.responseText,false);
        });
    }
    if( event.which === 76 && event.ctrlKey ) {
        event.preventDefault();
        initModal("modalQuick");
        CreateAJAX("/favourites/quick/list","GET","html",{"format":"select"})
        .done(function(response){
            displayModal("modalQuick","List of quick links",response,false);
            linkRows = $("table#tblLinks tr");
        })
        .fail(function(xhr){
            displayModal("modalQuick","Add to Quick Links",xhr.responseText,false);
        });
    	
    }

    else if ( event.which == 76 && event.ctrlKey ){
        alert("asdasdasdasd");
    }
});

$(document).on("click","#btnApply",function(){

    dialogMode = $("input#dialogMode").val();
    switch (dialogMode)
    {
        case "quickAdd":

            // Checking name field
            if ($("input#txtquickName").val() == ""){
                $("input#txtquickName").focus();
                return false;
            }

            // Creating new Quick Link
            CreateAJAX("/favourites/quick/create","POST","json",
                {"name":$("input#txtquickName").val(),"link":$("input#txtquickLink").val()})
            .done(function(response){$("div#modalQuick").modal("hide");})
            .fail(function(xhr){alert(xhr.responseText);})


            break;
        default:
            return false;
    }

});

$(document).on("keyup","input#txtSearch",function(){
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    linkRows.show().filter(function() {
        var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
    }).hide();
});
function generateLink(path){
    link = location.protocol + '//' + location.host + location.pathname+"?"
    for (var key in path) {
        if (path[key] != ""){
            link = link+key+"="+path[key]+"&";
        }
    }
    return link.substr(0,link.length-1);
}




