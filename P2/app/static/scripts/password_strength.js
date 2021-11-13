// Basado en ejemplo de Terrence Aluda en section.io

let strengthBadge = document.getElementById("fuerza_password");

// Una contraseña fuerte consta de al menos una minúscula, una mayúscula un
// dígito, un carácter especial (no alfanumérico) y al menos 8 caracteres en
// total
let strongPassword = new RegExp("(?=.*[a-z])"
                                + "(?=.*[A-Z])"
                                + "(?=.*[0-9])"
                                + "(?=.*[^A-Za-z0-9])"
                                + "(?=.{8,})");

// Una contraseña moderadamente fuerte consta de al menos 6 caracteres y cumple
// las demás condiciones
let mediumReq1 = "((?=.*[a-z])"
                 + "(?=.*[A-Z])"
                 + "(?=.*[0-9])"
                 + "(?=.*[^A-Za-z0-9])"
                 + "(?=.{6,}))";
//let mediumReq2 = "((?=.*[a-z])"
//                 + "(?=.*[A-Z])"
//                 + "(?=.*[^A-Za-z0-9])"
//                 + "(?=.{8,}))";
//let mediumPassword = new RegExp(mediumReq1 + "|" + mediumReq2);
let mediumPassword = new RegExp(mediumReq1);

//  StrengthChecker()
// Comprueba la fuerza de la contraseña introducida
$(function() {
    let originalBG = $("[name='reg_password']").css("background-color");
    $("#fuerza_password").hide();
    $("[name='reg_password']").keyup(function() {
        let strengthBadge = $(this).siblings("#fuerza_password");
        let passwordParameter = $(this).val();

        if (passwordParameter.length == 0) {
            strengthBadge.hide();
            $(this).css("background-color", originalBG);
        } else {
            strengthBadge.show();

            if (strongPassword.test(passwordParameter)) {
                $(this).css("background-color", "lightgreen");
                strengthBadge.css("color", "green");
                strengthBadge.text("Fuerte");
            } else if (mediumPassword.test(passwordParameter)) {
                $(this).css("background-color", "khaki");
                strengthBadge.css("color", "gold");
                strengthBadge.text("Normal");
            } else {
                $(this).css("background-color", "pink");
                strengthBadge.css("color", "red");
                strengthBadge.text("Débil");
            }
        }
    });
});
