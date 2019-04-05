
from src.resources import *
from src.utils import *
from src.imaging import *
from src.file_io import *
from src.analysis import *

import pytesseract
import time

from src.Screenshot import Screenshot

TESTING = False
DEBUG = False

save_data_with_debug = False  # if you want to save the data to the output file even though you're in debug mode
write_data_on_error = False  # if you want to write the data to the output file despite an error
save_all_images = True

do_analysis = True


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


# TODO: fix incorrect comparison with "4" etc.
def find_better_placement_value(placement1, placement2):
    if "#" in placement1:
        return placement1
    if "#" in placement2:
        return placement2

    for i in range(0, 20):
        if is_close_match(placement1, "#" + str(i), tolerance=1):
            return placement1
        if is_close_match(placement2, "#" + str(i), tolerance=1):
            return placement2
    return ""


def test_func():
    monitor_id = 1
    with mss.mss() as sct:
        mon = sct.monitors[monitor_id]
        height = mon["height"]
        width = mon["width"]

        monitor_area_1 = {
            "top": mon["top"] + int(0.12 * height),  # X px from the top
            "left": mon["left"] + int(0.112 * width),  # X px from the left
            "height": int(0.324 * height),
            "width": int(0.65 * width),
            "mon": monitor_id,
        }

    scrnshot = Screenshot(monitor_area_1)

    scrnshot.save("../test.png")


def main():

    if TESTING:
        test_func()
        return 0

    if do_analysis:
        main_graphs()
        return 0

    init_output_file()

    while True:

        if DEBUG:
            # Use test screenshot
            img_stats, img_placement = None, None
            cln_img_stats = clean_image_stats(Image.open(test_images_path + test_stats_name))
            cln_img_placement = clean_image_placement(Image.open(test_images_path + test_placement_name))
        else:
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
            img_stats, img_placement = take_screenshots(monitor_id=1)

            # Remove noise from screenshot
            cln_img_stats = clean_image_stats(img_stats)
            cln_img_placement = clean_image_placement(img_placement)

        # Detect text from denoised screenshot
        text_ocr_stats = pytesseract.image_to_string(cln_img_stats, lang="eng").lower().replace("\n\n", "\n")
        text_ocr_placement = pytesseract.image_to_string(cln_img_placement, lang=trained_data_name, config="--psm 13 -c tessedit_char_whitelist=0123456789")
        text_ocr_placement_alternative = pytesseract.image_to_string(cln_img_placement)
        print("---------------------------------------------------------")
        print(text_ocr_stats)
        print("Placement:", text_ocr_placement)
        print("Alternate Placement:", text_ocr_placement_alternative)
        print("---------------------------------------------------------")

        # Search for legend. legend names are selected from a set list (with some tolerance)
        legend = None
        for legend_name in legends:
            if close_match_in(legend_name, text_ocr_stats):
                legend = legend_name
                break

        # Cancel if no legend was found
        if not legend:
            print_error("No Apex Match Summary found!")
            play_failure_sound()
            continue

        # See example: https://rubular.com/r/A4j1odfYdw7TWZ
        # select all characters after "season" that until we match newline, carriage return, space or p
        # (season is followed by " played x mins ago")
        season = find_regex(r"[\n\r]*.*season *([^\n\r p]*)", text_ocr_stats)

        # Consider changing these to include erroneously recognized "revive ally", "damage done" etc.

        # match until newline, carriage return, parenthesis or square bracket
        # TODO: Fix (rare) detection of 190 as 180
        kills = find_regex(r"[\n\r]*.*kills [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        time_survived = find_regex(r"[\n\r]*.*time survived [{(\[]*([^\n\r)\]}]*)", text_ocr_stats)

        # match damage done or damage cone
        damage_done = find_regex(r"[\n\r]*.*damage [dcu]one [{(\[]*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        revives = find_regex(r"[\n\r]*.*revive a.*y [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        respawns = find_regex(r"[\n\r]*.*respawn a.*y [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        group_size = find_regex(r"[\n\r]*.*playing with friends [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)
        if group_size and group_size.isdigit():
            group_size = str(int(group_size) + 1)
        else:
            group_size = None

        # Read placement from other image
        # placement = find_better_placement_value(text_ocr_placement, text_ocr_placement_alternative).replace("#", "")
        placement = text_ocr_placement

        # order is determined by init_output_file
        data = [season, group_size, time_survived, legend, damage_done, kills, revives, respawns, placement]
        print("Season:", season)
        print("Placement:", placement)
        print("Legend:", legend.capitalize())
        print("Kills:", kills)
        print("Damage Done:", damage_done)
        print("Revives:", revives)
        print("Respawns:", respawns)
        print("Group Size:", group_size)
        print("Time Survived:", time_survived)

        # Check data for incorrect values, like None or non-digit values. Ignores the index value of the legend name
        data_correct = check_data(data)

        # Write data to output file and play sound
        if data_correct:
            if not is_equal_to_last_entry(data) and not (DEBUG and save_data_with_debug):
                append_to_output(data)
            else:
                print_warning("Duplicate entry")
            play_success_sound()
        elif write_data_on_error:
            play_invalid_value_sound()
            if not is_equal_to_last_entry(data) and not (DEBUG and save_data_with_debug):
                append_to_output(data)
            print_warning("Data invalid, written to output anyway.")
        else:
            # append_to_output(data)
            play_invalid_value_sound()
            print_error("Data invalid, was not written to output.")

        if save_all_images:
            cln_img_stats.save(output_images_path + clean_stats_name)
            cln_img_placement.save(output_images_path + clean_placement_name)
            if not DEBUG:
                img_stats.save(output_images_path + raw_stats_name)
                img_placement.save(output_images_path + raw_placement_name)
            print_special("Saved all images.")

        if DEBUG:
            return


if __name__ == "__main__":
    main()
