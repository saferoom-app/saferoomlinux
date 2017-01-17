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

    if ( event.which == 66 && event.ctrlKey ){
        $("div#modalServer").modal('show');
        CreateAJAX("/log","GET","html",{})
        .done(function(response){
            $("div#serverLog").html("<textarea rows='20' style='width:100%;height:100%'>"+response+"</textarea>");
        })
        .fail(function(xhr){
            $("div#serverLog").html("<textarea style='width:100%;height:100%'>"+xhr.responseText+"</textarea>");            
        });
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

            jsonString = JSON.stringify({"name":$("input#txtquickName").val(),"link":$("input#txtquickLink").val()});
            // Creating new Quick Link
            CreateAJAX("/favourites/quick/create","POST","json",jsonString)
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
    console.log(path);
    for (var key in path) {
        if (path[key] != ""){
            link = link+key+"="+path[key]+"&";
        }
    }
    console.log(link);
    return link.substr(0,link.length-1);
}




