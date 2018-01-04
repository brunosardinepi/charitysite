$(document).ready(function() {
    $('#donateModal').on('shown.bs.modal', function () {
        $('#id_amount').trigger('focus');
    });
});

$(document).on('change', "input.preset-amount", function() {
    console.log("input.preset-amount changed");
    $("input.preset-amount").not(this).prop("checked", false);
});

$(document).on('click', "#new-card", function(event) {
    event.preventDefault();
    $("#new-card-info").show();
    $("#new-card").text("Cancel new card");
    $("#new-card").attr("id", "hide-new-card");
});

$(document).on('click', "#hide-new-card", function(event) {
    event.preventDefault();
    $("#new-card-info").hide();
    $("#hide-new-card").text("New card");
    $("#hide-new-card").attr("id", "new-card");
});

var elements = stripe.elements();
var card = elements.create('card');

$(document).on('click', "[id^='show-donate']", function(event) {
    event.preventDefault();

    var arr = $(this).attr('id');
    var arr = arr.split("-");
    var model = arr[2];
    var pk = arr[3];

    var url = "/page/" + pk + "/donate/";

    $('#donateModal .modal-body').append("<form action=" + url + " method='POST' id='payment-form'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /><input type='checkbox' name='amount' class='preset-amount' value=5 />$5<br /><input type='checkbox' name='amount' class='preset-amount' value=10 />$10<br /><input type='checkbox' name='amount' class='preset-amount' value=25 />$25<br /><input type='checkbox' name='amount' class='preset-amount' value=50 />$50<br /><input type='checkbox' name='amount' class='preset-amount' value=100 />$100<br /><div class='input-group'><div class='input-group-prepend'><span class='input-group-text'>$</span></div><input type='number' class='form-control' name='amount' id='id_amount' min='0' max='999999' aria-label='Amount' placeholder='Custom amount'></div><div class='form-check'><input type='checkbox' name='anonymous_amount' class='form-check-input' id='id_anonymous_amount'><label class='form-check-label' for='id_anonymous_amount'>Anonymous amount</label></div><div id='amount-errors'></div><div class='form-check'><input type='checkbox' name='anonymous_donor' class='form-check-input' id='id_anonymous_donor'><label class='form-check-label' for='id_anonymous_donor'>Anonymous donor</label></div><div class='form-group'><textarea class='form-control' name='comment' id='id_comment' rows='3' placeholder='Type your comment here (optional)'></textarea></div>   <div class='form-group'><input type='text' class='form-control' name='first_name' id='id_first_name' max_length='255' placeholder='First name' required></div><div class='form-group'><input type='text' class='form-control' name='last_name' id='id_last_name' max_length='255' placeholder='Last name' required></div><label for='card-element'>Debit or Credit card</label><div id='card-element'></div><div id='card-errors' role='alert'></div></form>");
    card.mount("#card-element");

    card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    $('#donateModal .modal-footer').html("<button type='button' class='btn btn-secondary' data-dismiss='modal'>Close</button><button type='button' class='btn btn-primary submit-donate' data-dismiss='modal'>Donate</button>");
});

$(document).on("click", ".submit-donate", function(event) {
    donate();
});

function donate() {

            if (document.getElementById("id_anonymous_donor").checked) {
                var extraDetails = {};
            } else {
                var extraDetails = {
                    name: "{{ request.user.first_name }} {{ request.user.last_name }}",
                };
            };

                stripe.createToken(card, extraDetails).then(function(result) {
                    if (result.error) {
                        var errorElement = document.getElementById('card-errors');
                        errorElement.textContent = result.error.message;
                    } else {
                        stripeTokenHandler(result.token);
                    }
                });

                if (($("input.preset-amount:checked").length == 0) && ($("#id_amount").val().length == 0)) {
                    console.log("bad, nothing is checked and amount is empty");
                    $("#amount-errors").html("Please select an amount to donate.");
                } else {
                    console.log("good, something is either checked or the amount is not empty");
                    $("#amount-errors").html("");
                    var form = document.getElementById("payment-form");
                    form.submit();
                };
};

function stripeTokenHandler(token) {
    var form = document.getElementById("payment-form");
    var hiddenInput = document.createElement("input");
    hiddenInput.setAttribute("type", "hidden");
    hiddenInput.setAttribute("name", "stripeToken");
    hiddenInput.setAttribute("value", token.id);
    form.appendChild(hiddenInput);
    form.submit();
}
