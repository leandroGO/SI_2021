function user_count() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            document.getElementById("footer").innerHTML = xmlhttp.responseText;
        }
    };
    xmlhttp.open("GET", "/ajax", true);
    xmlhttp.send();
}

$(document).ready(function(){
    setInterval(user_count, 3000);
    user_count();
});
