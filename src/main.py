
from src.resources import *
from src.utils import *
from src.imaging import *
from src.file_io import *


import pytesseract
import time

DEBUG = False


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
            img_stats, img_placement = take_screenshots(monitor_id=1)

            # Remove noise from screenshot
            cln_img_stats = clean_image_stats(img_stats)
            cln_img_placement = clean_image_placement(img_placement)
        else:
            # Use test screenshot
            img_stats, img_placement = None, None
            cln_img_stats = clean_image_stats(Image.open(images_path + test_stats_name))
            cln_img_placement = clean_image_placement(Image.open(images_path + test_placement_name))

        # Detect text from denoised screenshot
        text_ocr_stats = pytesseract.image_to_string(cln_img_stats).lower().replace("\n\n", "\n")
        text_ocr_placement = pytesseract.image_to_string(cln_img_placement).lower()
        print("---------------------------------------------------------")
        print(text_ocr_stats)
        print("Placement:", text_ocr_placement)
        print("---------------------------------------------------------")

        # Handle text input
        if not close_match_in("xp breakdown", text_ocr_stats):
            print_error("No Apex Match Summary found!")
            play_failure_sound()
            continue

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
        season = find_regex(r"[\n\r].*season *([^\n\r p]*)", text_ocr_stats)

        # Consider changing these to include erroneously recognized "revive ally", "damage done" etc.

        # match until newline, carriage return, parenthesis or square bracket
        kills = find_regex(r"[\n\r].*kills [{(\[]x*([^\n\r)\]}]*)",
                           text_ocr_stats)  # TODO: Detects 190 as 180 sometimes o.o

        # see above
        time_survived = find_regex(r"[\n\r].*time survived [{(\[]*([^\n\r)\]}]*)", text_ocr_stats)

        # match damage done or damage cone
        damage_done = find_regex(r"[\n\r].*damage [dcu]one [{(\[]*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        revives = find_regex(r"[\n\r].*revive al*y [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        respawns = find_regex(r"[\n\r].*respawn al*y [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)

        # see above
        group_size = str(int(find_regex(r"[\n\r].*playing with friends [{(\[]x*([^\n\r)\]}]*)", text_ocr_stats)) + 1)

        # Read placement from other image
        placement = text_ocr_placement.replace("#", "")

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
            if not is_equal_to_last_entry(data):
                append_to_output(data)
            else:
                print_warning("Duplicate entry")
            play_success_sound()
        else:
            play_invalid_value_sound()
            # Save screenshot and denoised image
            cln_img_stats.save(images_path + clean_stats_name)
            cln_img_placement.save(images_path + clean_placement_name)
            if not DEBUG:
                img_stats.save(images_path + stats_name)
                img_placement.save(images_path + placement_name)
            print_error("Data incorrect, was not written to output.")

        if DEBUG:
            return


if __name__ == "__main__":
    main()
