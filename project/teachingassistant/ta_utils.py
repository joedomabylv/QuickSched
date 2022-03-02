"""Utility functions for the teachingassistant app."""


def availability_list_to_tuples(availability_list):
    """
    Create a list of tuples regarding a TA's availability.

    Takes a list of TA class times (availability) from the 'ta_info' form
    (views.py) in unordered format and create a list of tuples.
    """
    # ensure the length of the list is even
    if len(availability_list) % 2 == 0:
        new_list = []
        # the format of the input list is:
        # (start_time, end_time, start_time, end_time, ...)
        # index starts at 1 to get every element before as well as the current
        # index. index is incremented by 2 each iteration
        index = 1
        while index <= len(availability_list):
            item = (availability_list[index - 1],
                    availability_list[index])
            new_list.append(item)
            index += 2
        return new_list
    return None


def parse_availability(request, total_classes):
    """
    Parse through posted objects to get a TA's input availability.

    Takes the request object from Django and pulls POST data based on
    the total number of classes the TA submitted. The only way this function
    will be called is when the request is already confirmed to be of
    type "POST".
    """
    index = 0
    avail_list = []
    while index <= total_classes:
        avail = request.POST.getlist(f'ta_class_time_{index}')
        avail_list.append(avail)
        index += 1
    return avail_list
