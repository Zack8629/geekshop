"use strict";

window.onload = function () {
    console.log('DOM ready');
    $('.basket_record').on('change', "input[type='number']", function (event) {
        let quantity = event.target.value;
        let basketItemPk = event.target.name;
        console.log(basketItemPk, quantity);
        $.ajax({
            url: "/basket/update/" + basketItemPk + "/" + quantity + "/",
            success: function (data) {
                if (data.status) {
                    $('.basket_summary').html(data.basket_summary);
                }
            },
        });
    });
}
