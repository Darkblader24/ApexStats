import re
from threading import Thread

import pytesseract
import mss
import mss.tools
from PIL import Image

import keyboard  # check button presses
import datetime  # write date and time to output
import time
import winsound

DEBUG = False
legends = ["bloodhound", "gibraltar", "lifeline", "pathfinder", "octane",
           "wraith", "bangalore", "caustic", "mirage"]


def print_warning(*x, end="\n"):
    print("\033[93m", end="")
    for elem in x:
        print(str(elem), end=" ")
    print(end=end)
    print("\033[0m", end="")
    return


def print_error(*x, end="\n"):
    print("\033[31m", end="")
    for elem in x:
        print(str(elem), end=" ")
    print(end=end)
    print("\033[0m", end="")
    return


def check_quit():
    return keyboard.is_pressed("alt") and keyboard.is_pressed("q")


def clean_image(img):
    new_img_data = []
    color_black = (0, 0, 0)
    color_white = (255, 255, 255)

    for i, color in enumerate(img.convert("HSV").getdata()):
        if i % img.size[0] > img.size[0] * 0.92:
            new_img_data.append(color_white)
            continue
        h, s, v = color
        if (s <= 5 or s >= 204) and v > 104:
            new_img_data.append(color_black)
        elif s in range(56, 62) and v > 150:
            new_img_data.append(color_black)
        else:
            new_img_data.append(color_white)

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_img_data)
    return new_img


def play_success_sound():
    thread = Thread(target=winsound.PlaySound, args=["sounds/success.wav", winsound.SND_FILENAME])
    thread.start()


def play_failure_sound():
    # winsound.PlaySound("sounds/invalid_value.wav", winsound.SND_FILENAME)
    thread = Thread(target=winsound.MessageBeep, args=[winsound.MB_OK])
    thread.start()


def play_screenshot_sound():
    thread = Thread(target=winsound.PlaySound, args=["sounds/screenshot.wav", winsound.SND_FILENAME])
    thread.start()


def play_invalid_value_sound():
    thread = Thread(target=winsound.PlaySound, args=["sounds/invalid_value.wav", winsound.SND_FILENAME])
    thread.start()


def make_screenshot(monitor_id):
    print("Processing...")
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]

        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", (sct_img.size[0], round(sct_img.size[1] * 0.45)), sct_img.bgra, "raw", "BGRX")

        play_screenshot_sound()
    return img


def find_regex(expression, text):
    regex = re.findall(expression, text)
    if regex:
        # transform regex from list of tuples to list
        if isinstance(regex[-1], tuple):
            regex = [regex[i][j] for i in range(0, len(regex)) for j in range(0, len(regex[i]))]
        # accept only the last non-empty match (eases up writing regex)
        while not regex[-1]:
            regex = regex[:-1]
        return clean_data(regex[-1])
    return None


def is_close_match(s1, s2, tolerance=1, allow_different_length=True):
    """ returns whether or not two strings only differ by the number of tolerated characters """
    if s1 == s2:
        return True
    if not allow_different_length and len(s1) != len(s2):
        return False

    exhausted = abs(len(s1) - len(s2))
    for i in range(0, min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            exhausted += 1
        if exhausted > tolerance:
            return False

    return exhausted <= tolerance


def close_match_in(match, text, tolerance=1):
    """ returns whether or not a string is found as a close match within a text """
    if match in text:
        return True
    if len(match) >= len(text):
        return is_close_match(match, text, tolerance=tolerance)

    for i in range(0, len(text) - len(match)):
        if is_close_match(match, text[i:i + len(match)]):
            return True

    return False


def init_output_file(filepath="output/Apex Stats.txt", delim="\t"):
    # create a default output file with headers
    import os  # to check if the output file exists

    dir_path = "/".join(filepath.split("/")[:-1])
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    if not os.path.isfile(filepath):
        with open(filepath, "w+") as file:
            file.write("Initialized on: " + datetime.datetime.now().strftime("%d/%b/%Y, %H:%M:%S") + "\n")
            file.write(
                "Season" + delim + "Group-Size" + delim + "Time Survived" + delim + "Legend" + delim + "Damage" +
                delim + "Kills" + delim + "Revives" + delim + "Respawns" + delim + "Placement\n")
    return


def append_to_output(values, filepath="output/Apex Stats.txt", delim="\t"):
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


def is_equal_to_last_entry(values, filepath="output/Apex Stats.txt", delim="\t"):
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


def check_data(values):
    all_digits = True

    for i in range(0, len(values)):
        value = values[i]

        if not value:
            all_digits = False
            print_error("INVALID VALUE:", value)

        elif value not in legends and not value.replace(":", "").isdigit():
            all_digits = False
            print_error("INVALID VALUE:", value)

    return all_digits


def clean_data(val):
    """ manual cleaning of potentially incorrectly recognized values """
    val = val.replace("o", "0")
    val = val.replace("c", "0")
    val = val.replace("d", "0")
    val = val.replace("l", "1")
    val = val.replace(",", "")
    val = val.replace("/", "7")
    val = val.replace("t", "7")
    return val


def main():

    init_output_file()

    while True:

        if not DEBUG:
            print("---------------------------------------------------------")
            print("Waiting for input...")
            print("Press Alt + K to take a screenshot of your match summary.")

            # Check for input
            while True:
                if check_quit():
                    return
                # Take screenshot
                if keyboard.is_pressed("alt") and keyboard.is_pressed("k"):
                    break
                time.sleep(0.01)

            # Take a screenshot of the selected monitor
            img = make_screenshot(monitor_id=1)

            # Remove noise from screenshot
            cln_img = clean_image(img)
        else:
            # Use test screenshot
            img = None
            cln_img = clean_image(Image.open("input/apex_screenshot_test_half.png"))

        # Detect text from denoised screenshot
        text_ocr = pytesseract.image_to_string(cln_img).lower().replace("\n\n", "\n")
        print("---------------------------------------------------------")
        print(text_ocr)
        print("---------------------------------------------------------")

        # Handle text input
        if not close_match_in("xp breakdown", text_ocr):
            print_error("No Apex Match Summary found!")
            play_failure_sound()
            continue

        # See example: https://rubular.com/r/A4j1odfYdw7TWZ
        # select all characters after "season" that until we match newline, carriage return, space or p
        # (season is followed by " played x mins ago")
        season = find_regex(r"[\n\r].*season *([^\n\r p]*)", text_ocr)
        print("Season:", season)

        # match until newline, carriage return, comma, full-stop or space
        # OCR likes to detect the giant # as either ff or fe, so we have to check for those too
        # Lars' variant: [\n\r]match.*[#f][fe]?([^\n\r,. 'line']*)|squad.*[#f][fe]?([^\n\r,. 'line']*)|#([^\n\r., 'line'])
        placement = find_regex(r"[\n\r].*#([^\n\r,. )]*)|fe([^l\n\r,. )]*)|ff([^\n\r,. )]*)", text_ocr)
        # only 20 squads
        while placement and placement.isdigit() and int(placement) > 20:
            if placement.endswith("20"):
                placement = placement[:-2]
            else:
                placement = placement[:-1]
        print("Placement:", placement)

        # Consider changing these to include erroneously recognized "revive ally", "damage done" etc.

        # match until newline, carriage return, parenthesis or square bracket
        kills = find_regex(r"[\n\r].*kills [{(\[]x*([^\n\r)\]}]*)", text_ocr)
        print("Kills:", kills)

        # see above
        time_survived = find_regex(r"[\n\r].*time survived [{(\[]*([^\n\r)\]}]*)", text_ocr)
        print("Time Survived:", time_survived)

        # match damage done or damage cone
        damage_done = find_regex(r"[\n\r].*damage [dcu]one [{(\[]*([^\n\r)\]}]*)", text_ocr)
        print("Damage Done:", damage_done)

        # see above
        revives = find_regex(r"[\n\r].*revive ally [{(\[]x*([^\n\r)\]}]*)", text_ocr)
        print("Revives:", revives)

        # see above
        respawns = find_regex(r"[\n\r].*respawn ally [{(\[]x*([^\n\r)\]}]*)", text_ocr)
        print("Respawns:", respawns)

        # see above
        group_size = str(int(find_regex(r"[\n\r].*playing with friends [{(\[]x*([^\n\r)\]}]*)", text_ocr)) + 1)
        print("Group Size:", group_size)

        # legend names are selected from a set list (with some tolerance)
        legend = None
        for legend_name in legends:
            if close_match_in(legend_name, text_ocr):
                legend = legend_name
                break
        print("Legend:", legend.capitalize())

        # order is determined by init_output_file
        data = [season, group_size, time_survived, legend, damage_done, kills, revives, respawns, placement]

        # Check data for incorrect values, like None or non-digit values. Ignores the index value of the legend name
        data_correct = check_data(data)

        # Write data to output file and play sound
        if data_correct:
            if not is_equal_to_last_entry(data):
                append_to_output(data)
            else:
                print_warning("Duplicate entry")
            play_success_sound()
        else:
            play_invalid_value_sound()
            # Save screenshot and denoised image
            cln_img.save("input/apex_stats_clean.png")
            if not DEBUG:
                img.save("input/apex_screenshot.png")
            print_error("Data incorrect, was not written to output.")

        if DEBUG:
            return


if __name__ == "__main__":
    main()
