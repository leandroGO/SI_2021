$(function() {
    $(".detalle_compra").hide();
    $(".historial tr").click(function() {
        $(this).find(".detalle_compra").toggle(200);
    });
});
