import re
import pytesseract
import mss
import mss.tools
from PIL import Image

import keyboard  # check button presses
import datetime  # write date and time to output


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


def make_screenshot(monitor_id):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]

        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", (sct_img.size[0], round(sct_img.size[1] * 0.45)), sct_img.bgra, "raw", "BGRX")
    return img


def find_regex(expression, text):
    result = None
    regex = re.findall(expression, text)
    if regex:
        result = regex[-1].replace("d", "0").replace("o", "0").replace("O", "0")
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
    if not os.path.isfile(filepath):
        with open(filepath, "w") as file:
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


def clean_data(values):
    """ manual cleaning of potentially incorrectly recognized values """
    # Season should be a number
    return


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

            # Take a screenshot of the selected monitor
            img = make_screenshot(monitor_id=1)

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
        print(text_ocr)
        print("---------------------------------------------------------")

        # Handle text input
        if "xp breakdown" not in text_ocr:
            print("No Apex Match Summary found!")
            continue

        # See example: https://rubular.com/r/A4j1odfYdw7TWZ
        season = find_regex(r"[\n\r].*season *([^\n\r]*)", text_ocr)
        print("Season:", season)

        placement = find_regex(r"[\n\r].*# *([^\n\r.]*)", text_ocr)
        print("Placement:", placement)

        kills = find_regex(r"[\n\r].*kills [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Kills:", kills)

        time_survived = find_regex(r"[\n\r].*time survived [(\[]*([^\n\r)\]]*)", text_ocr)
        print("Time Survived:", time_survived)

        damage_done = find_regex(r"[\n\r].*damage [dc]one [(\[]*([^\n\r)\]]*)", text_ocr)
        print("Damage Done:", damage_done)

        revives = find_regex(r"[\n\r].*revive ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Revives:", revives)

        respawns = find_regex(r"[\n\r].*respawn ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Respawns:", respawns)

        group_size = find_regex(r"[\n\r].*playing with friends [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("Group Size:", group_size)

        legend = None
        for legend_name in legends:
            if close_match_in(legend_name, text_ocr):
                legend = legend_name
                break
        print("Legend:", legend.capitalize())

        # order is determined by init_output_file
        data = [season, group_size, legend, damage_done, kills, revives, respawns, placement]

        clean_data(data)
        append_to_output(data)

        if DEBUG:
            return


if __name__ == "__main__":
    main()
