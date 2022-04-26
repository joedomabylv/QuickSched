function to_template(student_id, course_id, time, year, version_number) {
    $.ajax({
	url: 'assign_to_template',
	type: 'GET',
	data: {
	    'student_id': student_id,
	    'course_id': course_id,
	    'time': time,
	    'year': year,
	    'version': version_number
	},
    });

    // update the history tab
    var history_list = document.getElementById('history_list');
    var warning_string = "You\'ve recently made a manual change! This change will be reverted first. Refresh the page to see it!";
    var old_html = history_list.innerHTML;

    if (!old_html.startsWith(warning_string)) {
	history_list.innerHTML = warning_string + old_html;	
    }
}
