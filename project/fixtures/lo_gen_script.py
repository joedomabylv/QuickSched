#!/usr/bin/env python3
import random
import json
import string

SEMESTER_NUMBER = 10
LABS_PER_SEMESTER = 10

seasons = ["SPR", "SUM", "FAL", "WNT"]
days = ["M", "T", "W", "Th", "F"]

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return (result_str)

# templates for how the objects will be written
semester_temp = {
    "model": "laborganizer.semester",
    "pk": 0,
    "fields": {
        "year": 0,
        "semester_time": ""
    }
}

template_temp = {
    "model": "optimization.templateschedule",
    "pk": 0,
    "fields": {
	"semester": 0
    }
}

lab_temp = {
    "model": "laborganizer.lab",
    "pk": 0,
    "fields": {
	"class_name": "",
	"subject": "",
	"catalog_id": "",
	"course_id": "",
	"section": "",
	"days": "",
	"facility_id": "",
	"facility_building": "",
	"instructor": "",
	"start_time": "",
	"end_time": "",
	"semester": 0
    }
}

# open file for writing
with open("dummy-lo.json", "w") as f:

        f.write("[")
        f.write("\n\n")
        # generate the semesters randomly
        index = 0
        lab_index = 0
        while index < SEMESTER_NUMBER:

                # set random values for semester object
                semester_temp["pk"] = index
                semester_temp["fields"]["year"] = random.randint(1000, 10000)
                semester_temp["fields"]["semester_time"] = random.choice(seasons)

                # set them according to their respective template schedule
                template_temp["pk"] = index
                template_temp["fields"]["semester"] = index

                # write both objects to file
                f.write(json.dumps(semester_temp, indent=4))
                f.write(",")
                f.write("\n\n")

                f.write(json.dumps(template_temp, indent=4))
                f.write(",")
                f.write("\n\n")

                sub_index = 0

                while sub_index < LABS_PER_SEMESTER:
                    s_hour = random.randint(1, 23)
                    s_minute_raw = random.randint(1, 59)
                    s_minute = f"{s_minute_raw:02}"

                    e_hour = random.randint(1, 23)
                    e_minute_raw = random.randint(1, 59)
                    e_minute = f"{e_minute_raw:02}"

                    # set random values for each object
                    lab_temp["pk"] = lab_index
                    lab_temp["fields"]["class_name"] = get_random_string(12)
                    lab_temp["fields"]["subject"] = get_random_string(4)
                    lab_temp["fields"]["catalog_id"] = str(random.randint(100, 1000))
                    lab_temp["fields"]["course_id"] = str(random.randint(1000, 10000))
                    lab_temp["fields"]["section"] = str(random.randint(100, 1000))
                    lab_temp["fields"]["days"] = " ".join(random.sample(days, 3))
                    lab_temp["fields"]["facility_id"] = str(random.randint(100, 1000))
                    lab_temp["fields"]["facility_building"] = get_random_string(12)
                    lab_temp["fields"]["instructor"] = get_random_string(12)
                    lab_temp["fields"]["start_time"] = str(s_hour) + ":" + str(s_minute)
                    lab_temp["fields"]["end_time"] = str(e_hour) + ":" + str(e_minute)
                    lab_temp["fields"]["semester"] = index


                    f.write(json.dumps(lab_temp, indent=4))
                    if index == SEMESTER_NUMBER - 1 and sub_index == LABS_PER_SEMESTER - 1:
                        f.write("\n\n")
                    else:
                        f.write(",")
                    f.write("\n\n")

                    sub_index += 1
                    lab_index += 1

                index += 1

        f.write("]")
        f.write("\n\n")
