class_time_form = document.getElementById('class_time_form')

function new_class_element() {
    class_time_form.innerHTML += "<div class=\"input-group mb-3\">\
 	                              <span class=\"input-group-text\">Start Time</span>\
	                              <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time[]\" required>\
	                              <span class=\"input-group-text\">End Time</span>\
	                              <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time[]\" required>\
	                              </div>"
}
