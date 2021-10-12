function user_count() {
	xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		document.getElementById("footer").innerHTML = xmlhttp.responseText;
		setTimeout(user_count, 30000);
	};
	xmlhttp.open("GET", "/ajax", true);
	xmlhttp.send();
}

$(document).ready(function(){
	user_count();
});
