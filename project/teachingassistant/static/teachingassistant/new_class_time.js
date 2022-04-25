var class_input_form = document.getElementById('class_input_form')
var submit_button = document.getElementById('submit_button')
var class_numbers = 0

function new_class_element() {
    // increment total class form count
    class_numbers += 1
    submit_button.value = class_numbers
    class_input_form.innerHTML += "<div class=\"container mt-3\">\
		<div class=\"row\">\
		    <div class=\"col-12\">\
			<div class=\"input-group\">\
			    <span class=\"input-group-text\">Start and end time</span>\
			    <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time_" + class_numbers + "\" required>\
			    <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time_" + class_numbers + "\" required>\
			</div>\
		    </div>\
		</div>\
		<div class=\"row\">\
		    <div class=\"col-12\">\
			<div class=\"input-group\">\
			    <span class=\"input-group-text\">Which semester?</span>\
			    <input type=\"text\" class=\"form-control\" placeholder=\"e.g. SPR2022\" name=\"ta_class_semester_" + class_numbers + "\" required>\
			</div>\
		    </div>\
		</div>\
		<!-- Day Selection -->\
		<div id=\"class_input_form\">\
		    <div class=\"row\">\
			<div class=\"col-12 mt-1\">\
			    <div class=\"form-check form-check-inline\">\
				<input class=\"form-check-input\" type=\"checkbox\" id=\"monday-check\" value=\"M\" name=\"ta_class_time_" + class_numbers + "\">\
				<label class=\"form-check-label\" for=\"monday-check\">M</label>\
			    </div>\
			    <div class=\"form-check form-check-inline\">\
				<input class=\"form-check-input\" type=\"checkbox\" id=\"tuesday-check\" value=\"T\" name=\"ta_class_time_" + class_numbers + "\">\
				<label class=\"form-check-label\" for=\"tuesday-check\">T</label>\
			    </div>\
			    <div class=\"form-check form-check-inline\">\
				<input class=\"form-check-input\" type=\"checkbox\" id=\"wednesday-check\" value=\"W\" name=\"ta_class_time_" + class_numbers + "\">\
				<label class=\"form-check-label\" for=\"wednesday-check\">W</label>\
			    </div>\
			    <div class=\"form-check form-check-inline\">\
				<input class=\"form-check-input\" type=\"checkbox\" id=\"thursday-check\" value=\"Th\" name=\"ta_class_time_" + class_numbers + "\">\
				<label class=\"form-check-label\" for=\"thursday-check\">Th</label>\
			    </div>\
			    <div class=\"form-check form-check-inline\">\
				<input class=\"form-check-input\" type=\"checkbox\" id=\"friday-check\" value=\"F\" name=\"ta_class_time_" + class_numbers + "\">\
				<label class=\"form-check-label\" for=\"friday-check\">F</label>\
			    </div>\
			</div>\
		    </div>\
		</div>\
		<!-- End Day Selection -->\
	    </div>"
}
