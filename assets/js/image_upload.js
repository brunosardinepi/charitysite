$(function () {
    $("#upload-button").click(function () {
        $("#upload-input").click();
    });

    $("#upload-input").fileupload({
        dataType: 'json',
        done: function (event, data) {
            if (data.result.is_valid == 't') {
                if(!$(".col-4").length) {
                    $("#no-images").remove();
                };
                $("#image-list").prepend("<div class='col-4' id='image-" + data.result.pk + "'><div class='card' style='border:0;'><img class='card-img-top' src='" + data.result.url + "'><div class='card-body p-0 pt-1'><div class='row justify-content-between'><div class='col'><span class='small profile' id='profile-" + data.result.pk + "'><a class='set-profile-picture' href=''>Make profile picture</a></span></div><div class='col-3 text-right'><a id='delete-" + data.result.pk + "' class='delete-image' href=''><i class='fal fa-trash-alt'></i></a></div></div></div></div></div>");
            } else {
                if (data.result.redirect == "error_size") {
                    var url = "/error/image/size/";
                } else if (data.result.redirect == "error_type") {
                    var url = "/error/image/type/";
                };
                window.location.href = url;
            };
        }
    });
});
