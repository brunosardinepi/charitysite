$(document).on("click", ".set-default", function(event) {
    event.preventDefault();
    var url = "/donation/card/default/";
    var id = $(this).closest("span").attr("id");
    $.ajax({
        url : url,
        type : "POST",
        traditional: true,
        data : {
            id : id
        },
        success : function(json) {
            $(".default").html("<a class='set-default' href=''>Set default</a>");
            $("#default-" + json.id).text("Default");
        }
    });
});

