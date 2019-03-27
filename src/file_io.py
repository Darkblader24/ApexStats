
import datetime  # write date and time to output

from src.resources import *


def is_equal_to_last_entry(values, filepath=output_path + output_stats_name, delim="\t"):
    # Checks if the last entry in the stats file equals the new to be written entry
    with open(filepath, "r") as file:
        data = file.read()

    # Skip if the file only consists of the first two lines
    data = data.split("\n")
    if len(data) <= 2:
        return False

    # Check the last and second to last entries, in case the last line is empty
    data1 = data[-1].split(delim)
    data2 = data[-2].split(delim)
    if len(data1) == len(values):
        data = data1
    elif len(data2) == len(values) and "Season" not in data2:
        data = data2
    else:
        return False

    # Compare the last and new entries
    for i in range(len(values)):
        if data[i] != values[i].capitalize():
            return False

    # Return true if they are truly equal
    return True


def init_output_file(filepath=output_path + output_stats_name, delim="\t"):
    # create a default output file with headers
    import os  # to check if the output file exists

    dir_path = "/".join(filepath.split("/")[:-1])
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    if not os.path.isdir(output_images_path):
        os.mkdir(output_images_path)

    if not os.path.isfile(filepath):
        with open(filepath, "w+") as file:
            file.write("\"Initialized on: " + datetime.datetime.now().strftime("%d/%b/%Y, %H:%M:%S") + "\n")
            file.write(
                "Season" + delim + "Group-Size" + delim + "Time Survived" + delim + "Legend" + delim + "Damage" +
                delim + "Kills" + delim + "Revives" + delim + "Respawns" + delim + "Placement\n")


def append_to_output(values, filepath=output_path + output_stats_name, delim="\t"):
    # write all values to the output file in given order
    with open(filepath, "a") as file:
        for i in range(0, len(values)):
            value = values[i]
            if not value:
                value = "NONE"
            file.write(value.capitalize())
            if i != len(values) - 1:
                file.write(delim)
        file.write("\n")
        return
