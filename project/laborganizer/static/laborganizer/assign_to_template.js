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
}
