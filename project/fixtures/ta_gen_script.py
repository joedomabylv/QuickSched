#!/usr/bin/env python3
import random
import json
import string

TA_NUMBER = 10
CONTRACTED = 7
CLASSES_PER_TA = 3

years = ["FR", "SO", "JR", "SR", "GR"]
days = ["M", "T", "W", "Th", "F"]

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return (result_str)

# templates for how the objects will be written
ta_temp = {
    "model": "teachingassistant.ta",
    "pk": 0,
    "fields": {
        "first_name": "",
        "last_name": "",
        "student_id": "",
        "contracted": False,
        "experience": "",
        "year": "",
        "holds_key": 0,
        "availability_key": 50
    }
}

availability_temp = {
    "model": "teachingassistant.availability",
    "pk": 0,
    "fields": {
	"class_times": [],
	"ta": 0
    }
}

holds_temp =     {
    "model": "teachingassistant.holds",
    "pk": 0,
    "fields": {
	"incomplete_profile": False,
	"update_availability": False,
	"update_experience": False,
	"ta": 0
    }
}




classtime_temp = {
    "model": "teachingassistant.classtime",
    "pk": 0,
    "fields": {
	"ta": 0,
	"start_time": "",
	"end_time": "",
	"days": ""
    }
}


# open file for writing
with open("dummy-ta.json", "w") as f, open("dummy-lo.json", "r") as j:

        classes = []
        semesters = []
        semester_num = 0
        json_data = json.load(j)
        for obj in json_data:
            if "catalog_id" in obj["fields"]:
                subject = obj["fields"]["subject"]
                catalog_id = obj["fields"]["catalog_id"]
                classes.append(subject + catalog_id)
            if obj["model"] == "laborganizer.semester":
                semester_num += 1

        semester_list = list(range(0,semester_num))
        print(semester_list)

        f.write("[")
        f.write("\n\n")
        # generate the semesters randomly
        index = 0
        class_time_pk = 0
        contracted = True
        while index < TA_NUMBER:

                if index > CONTRACTED:
                    contracted = False

                availability_temp["fields"]["class_times"].clear()

                # set random values for semester object
                ta_temp["pk"] = index
                ta_temp["fields"]["first_name"] = get_random_string(7)
                ta_temp["fields"]["last_name"] = get_random_string(7)
                ta_temp["fields"]["student_id"] = str(random.randint(1000, 9999))
                ta_temp["fields"]["contracted"] = contracted
                ta_temp["fields"]["experience"] = random.sample(classes, 3)
                ta_temp["fields"]["year"] = random.choice(years)
                ta_temp["fields"]["holds_key"] = index
                ta_temp["fields"]["availability_key"] = index
                ta_temp["fields"]["assigned_semesters"] = semester_list

                # set them according to their respective template schedule
                holds_temp["pk"] = index
                holds_temp["fields"]["ta"] = index

                # write both objects to file
                f.write(json.dumps(ta_temp, indent=4))
                f.write(",")
                f.write("\n\n")

                f.write(json.dumps(holds_temp, indent=4))
                f.write(",")
                f.write("\n\n")

                sub_index = 0

                while sub_index < CLASSES_PER_TA:
                    s_hour = random.randint(1, 23)
                    s_minute_raw = random.randint(1, 59)
                    s_minute = f"{s_minute_raw:02}"

                    e_hour = random.randint(1, 23)
                    e_minute_raw = random.randint(1, 59)
                    e_minute = f"{e_minute_raw:02}"

                    # set random values for each object
                    classtime_temp["pk"] = class_time_pk
                    classtime_temp["fields"]["ta"] = index
                    classtime_temp["fields"]["start_time"] = str(s_hour) + ":" + str(s_minute)
                    classtime_temp["fields"]["end_time"] = str(e_hour) + ":" + str(e_minute)
                    classtime_temp["fields"]["days"] = random.sample(days, 3)


                    f.write(json.dumps(classtime_temp, indent=4))
                    f.write(",")
                    f.write("\n\n")

                    availability_temp["fields"]["class_times"].append(class_time_pk)

                    sub_index += 1
                    class_time_pk += 1

                availability_temp["pk"] = index
                availability_temp["fields"]["ta"] = index

                f.write(json.dumps(availability_temp, indent=4))

                if index != TA_NUMBER - 1:
                    f.write(",")
                f.write("\n\n")

                index += 1

        f.write("]")
        f.write("\n\n")
