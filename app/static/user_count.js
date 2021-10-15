function user_count() {
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        document.getElementById("footer").innerHTML = xmlhttp.responseText;
    };
    xmlhttp.open("GET", "/ajax", true);
    xmlhttp.send();
}

$(document).ready(function(){
    setInterval(user_count, 30000);
    user_count();
});
