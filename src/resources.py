
import winsound
from threading import Thread


legends = ["bloodhound", "gibraltar", "lifeline", "pathfinder", "octane",
           "wraith", "bangalore", "caustic", "mirage"]

images_path = "input/"

stats_name = "raw_stats.png"
placement_name = "raw_placement.png"
clean_stats_name = "clean_stats.png"
clean_placement_name = "clean_placement.png"

test_stats_name = "test_stats.png"
test_placement_name = "test_placement.png"

trained_data_name = "TT"


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
