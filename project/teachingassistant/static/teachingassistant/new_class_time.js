var class_input_form = document.getElementById('class_input_form')
var submit_button = document.getElementById('submit_button')
var class_numbers = 0

function new_class_element() {
    // increment total class form count
    class_numbers += 1
    submit_button.value = class_numbers
    console.log(submit_button)
    class_input_form.innerHTML += "<label id=\"class_time_form\" for=\"ta_class_time_" + class_numbers + "\">\
	      <div class=\"input-group mb-3\">\
		  <!-- Time Selection -->\
		  <span class=\"input-group-text\">Start Time</span>\
		  <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time_" + class_numbers + "\" required>\
		  <span class=\"input-group-text\">End Time</span>\
		  <input type=\"time\" class=\"form-control\" value=\"12:00\" name=\"ta_class_time_" + class_numbers + "\" required>\
		  <!-- End Time Selection -->\
		  <!-- Day Selection -->\
		  <span class=\"input-group-text\">Days</span>\
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
		  <!-- End Day Selection -->\
	      </div>\
	  </label>"
}
