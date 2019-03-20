import re
import pytesseract
import mss
import mss.tools
from PIL import Image

import keyboard


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
    regex = re.findall(expression, text)
    if regex:
        return regex[0]
    return None


def main():
    while True:
        if check_quit():
            return

        while True:
            if check_quit():
                return
            if keyboard.is_pressed("alt") and keyboard.is_pressed("k"):
                break

        # Make a screenshot of the selected monitor
        # img = make_screenshot(monitor_id=1)

        # Remove noise from screenshot
        # cln_img = clean_image(img)
        cln_img = clean_image(Image.open("data/apex_screenshot_test_half.png"))

        # Save screenshot and denoised image
        # img.save("data/apex_screenshot.png")
        cln_img.save("data/apex_stats_clean.png")

        # Detect text from denoised screenshot
        text_ocr = pytesseract.image_to_string(cln_img).lower()
        print(text_ocr)

        # Handle text data
        if "xp breakdown" not in text_ocr:
            print("No Apex Match Summary found!")
            continue

        print("\n"
              "\n"
              "\n###########################"
              "\n###### MATCH SUMMARY ######"
              "\n###########################"
              "\n")

        legends = ["bloodhound", "gibraltar", "lifeline", "pathfinder", "octane",
                   "wraith", "bangalore", "caustic", "mirage"]

        time_survived = find_regex(r"[\n\r].*time survived [(\[]*([^\n\r)\]]*)", text_ocr)
        print("time survived:", time_survived)

        kills = find_regex(r"[\n\r].*kills [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("kills:", kills)

        damage_done = find_regex(r"[\n\r].*damage done [(\[]*([^\n\r)\]]*)", text_ocr)
        print("damage done:", damage_done)

        revives = find_regex(r"[\n\r].*revive ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("revives:", revives)

        respawns = find_regex(r"[\n\r].*respawn ally [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("respawns:", respawns)

        solo = find_regex(r"[\n\r].*playing with friends [(\[]x*([^\n\r)\]]*)", text_ocr)
        print("solo:", solo)

        placement = find_regex(r"[\n\r].*#*([^\n\r]*)", text_ocr)
        print("place:", placement)

        legend = None
        for legend_name in legends:
            if legend_name in text_ocr:
                legend = legend_name
                break
        print("legend:", legend)


if __name__ == "__main__":
    main()
