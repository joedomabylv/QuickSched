function count_labs() {
    // get the hidden lab number counter
    var lab_number_element = document.getElementById("number_of_labs");

    if (lab_number_element != null) {

	// get the total number of labs
	var number_of_labs = document.getElementsByClassName("lab").length;

	// assign the number of labs to the input elements value
	lab_number_element.value = number_of_labs;
    }
}

// run the above function on page load
window.onload = count_labs;
