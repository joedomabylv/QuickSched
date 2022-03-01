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
