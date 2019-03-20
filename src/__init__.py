import re
import pytesseract
import mss
import mss.tools
from PIL import Image

import keyboard


DEBUG = True
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


def close_match_in(string, text, tolerance=1):
    """ returns whether or not a string is found as a close match within a text """
    if string in text:
        return True
    if len(string) >= len(text):
        return is_close_match(string, text, tolerance=tolerance)

    for i in range(0, len(text) - len(string)):
        if is_close_match(string, text[i:i + len(string)]):
            return True

    return False


def main():

    while True:
        if not DEBUG:
            # Check for input
            while True:
                # Quit
                if check_quit():
                    return
                # Make screenshot
                if keyboard.is_pressed("alt") and keyboard.is_pressed("k"):
                    break

            # Make a screenshot of the selected monitor
            img = make_screenshot(monitor_id=1)

            # Remove noise from screenshot
            cln_img = clean_image(img)
        else:
            # Use test screenshot
            cln_img = clean_image(Image.open("data/apex_screenshot_test_half.png"))

        # Save screenshot and denoised image
        img.save("data/apex_screenshot.png")
        cln_img.save("data/apex_stats_clean.png")

        # Detect text from denoised screenshot
        text_ocr = pytesseract.image_to_string(cln_img).lower().replace("\n\n", "\n")
        print(text_ocr)
        print("---------------------------------------------------------")

        # Handle text data
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
            # if legend_name in text_ocr:
            #     legend = legend_name
            #     break
        print("Legend:", legend.capitalize())

        if DEBUG:
            return


if __name__ == "__main__":
    main()
