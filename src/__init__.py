import re
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


def check_quit():
    return keyboard.is_pressed("alt") and keyboard.is_pressed("q")


def clean_image(img):
    new_img_data = []

    for i, color in enumerate(img.convert("HSV").getdata()):
        h, s, v = color
        if (s <= 5 or s >= 204) and v > 127:
            new_img_data.append((0, 0, 0))
        elif s in range(56, 62) and v > 150:
            new_img_data.append((0, 0, 0))
        else:
            new_img_data.append((255, 255, 255))

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_img_data)
    return new_img


def play_success_sound():
    winsound.PlaySound("sounds/success.wav", winsound.SND_FILENAME)
    return


def play_failure_sound():
    # winsound.PlaySound("sounds/failed.wav", winsound.SND_FILENAME)
    winsound.MessageBeep(winsound.MB_OK)
    return


def play_screenshot_sound():
    winsound.PlaySound("sounds/screenshot.wav", winsound.SND_FILENAME)
    return


def make_screenshot(monitor_id):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]

        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", (sct_img.size[0], round(sct_img.size[1] * 0.45)), sct_img.bgra, "raw", "BGRX")

        play_screenshot_sound()
    return img


def find_regex(expression, text):
    result = None
    regex = re.findall(expression, text)
    if regex:
        result = clean_data(regex[-1])
    return result


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
                "Season" + delim + "Group-Size" + delim + "Legend" + delim + "Damage" + delim + "Kills" + delim + "Revives" + delim + "Respawns" + delim + "Placement\n")
    return


def append_to_output(values, filepath="output/Apex Stats.txt", delim="\t"):
    # write all values to the output file in given order
    with open(filepath, "a") as file:
        for i in range(0, len(values)):
            file.write(values[i])
            if i != len(values) - 1:
                file.write(delim)
        file.write("\n")
    return


def clean_data(val):
    """ manual cleaning of potentially incorrectly recognized values """
    result = val.replace("o", "0").replace("d", "0").replace(",", "")
    return result


def main():

    init_output_file()

    while True:
        if not DEBUG:
            # Check for input
            while True:
                if check_quit():
                    return
                # Take screenshot
                if keyboard.is_pressed("alt") and keyboard.is_pressed("k"):
                    break
                time.sleep(0.01)


            # Take a screenshot of the selected monitor
            img = make_screenshot(monitor_id=3)

            # Remove noise from screenshot
            cln_img = clean_image(img)
        else:
            # Use test screenshot
            cln_img = clean_image(Image.open("input/apex_screenshot_test_half.png"))

        # Save screenshot and denoised image
        # img.save("input/apex_screenshot.png")
        cln_img.save("input/apex_stats_clean.png")

        # Detect text from denoised screenshot
        text_ocr = pytesseract.image_to_string(cln_img).lower().replace("\n\n", "\n")
        print("---------------------------------------------------------")
        print(text_ocr)
        print("---------------------------------------------------------")

        # Handle text input
        if not close_match_in("xp breakdown", text_ocr):
            print("No Apex Match Summary found!")
            play_failure_sound()
            continue

        # See example: https://rubular.com/r/A4j1odfYdw7TWZ
        # select all characters after "season" that until we match newline, carriage return, space or p (season is followed by " played x mins ago")
        season = find_regex(r"[\n\r].*season *([^\n\r p]*)", text_ocr)
        print("Season:", season)

        # match until newline, carriage return, comma, full-stop or space
        placement = find_regex(r"[\n\r].*# *([^\n\r., ]*)", text_ocr)
        if int(placement) > 20:
            placement = placement[:-2]
        print("Placement:", placement)

        # Consider changing these to include erroneously recognized "revive ally", "damage done" etc.

        # match until newline, carriage return, parenthesis or square bracket
        kills = find_regex(r"[\n\r].*kills [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Kills:", kills)

        # see above
        time_survived = find_regex(r"[\n\r].*time survived [(\[]*([^\n\r)\]]*)", text_ocr)
        print("Time Survived:", time_survived)

        # match damage done or damage cone
        damage_done = find_regex(r"[\n\r].*damage [dc]one [(\[]*([^\n\r)\]]*)", text_ocr)
        print("Damage Done:", damage_done)

        # see above
        revives = find_regex(r"[\n\r].*revive ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Revives:", revives)

        # see above
        respawns = find_regex(r"[\n\r].*respawn ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Respawns:", respawns)

        # see above
        group_size = str(int(find_regex(r"[\n\r].*playing with friends [(\[]x*([^\n\r)\]]*)", text_ocr)) + 1)
        print("Group Size:", group_size)

        # legend names are selected from a set list (with some tolerance)
        legend = None
        for legend_name in legends:
            if close_match_in(legend_name, text_ocr):
                legend = legend_name
                break
        print("Legend:", legend.capitalize())

        # order is determined by init_output_file
        data = [season, group_size, legend, damage_done, kills, revives, respawns, placement]

        append_to_output(data)
        play_success_sound()

        if DEBUG:
            return


if __name__ == "__main__":
    main()
