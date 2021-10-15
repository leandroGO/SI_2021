let specialChar = new RegExp("(?=.*[^A-Za-z0-9])");
let minPasswordLenght = 8

function regValidate() {
    let regForm = document.forms["register_form"];

    if (specialChar.test(regForm["reg_user"].value)) {
        alert("El nombre de usuario no admite caracteres especiales ni espacios.");
        return false;
    }
    if (regForm["reg_password"].value.length < minPasswordLenght) {
        alert("La contraseña es muy corta (debe tener al menos " +
            minPasswordLenght + " caracteres).");
        return false;
    }
    if (regForm["reg_password"].value != regForm["reg_confirm"].value) {
        alert("La contraseña y su confirmación no coinciden.");
        return false;
    }
    if (! /^\d*$/.test(regForm["reg_tarjeta"].value)) {
        alert("El número de tarjeta de crédito solo admite dígitos (0-9).");
        return false;
    }
}
