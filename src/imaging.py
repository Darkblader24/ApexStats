
from PIL import Image
import mss
import mss.tools
from src.resources import play_screenshot_sound


def take_screenshot(sct, monitor):
    sct_img = sct.grab(monitor)
    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")


def take_screenshots(monitor_id):
    print("Processing...")
    with mss.mss() as sct:
        mon = sct.monitors[monitor_id]
        height = mon["height"]
        width = mon["width"]

        monitor_area_1 = {
            "top": mon["top"] + int(0.12*height),    # X px from the top
            "left": mon["left"] + int(0.112*width),  # X px from the left
            "height": int(0.324*height),
            "width": int(0.65*width),
            "mon": monitor_id,
        }
        img1 = take_screenshot(sct, monitor_area_1)

        monitor_area_2 = {
            "top": mon["top"] + 0,
            "left": mon["left"] + int(0.766*width),
            "height": int(0.157*height),
            "width": int(0.115*width),
            "mon": monitor_id,
        }
        img2 = take_screenshot(sct, monitor_area_2)

        play_screenshot_sound()
    return img1, img2


def clean_image_stats(img):
    new_img_data = []
    color_black = (0, 0, 0)
    color_white = (255, 255, 255)

    for i, color in enumerate(img.convert("HSV").getdata()):
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


def clean_image_placement(img):
    new_img_data = []
    color_black = (0, 0, 0)
    color_white = (255, 255, 255)

    x, y = img.size
    min_placement_x = 0

    for i, color in enumerate(img.convert("HSV").getdata()):
        h, s, v = color
        if h in range(9, 11):
            # When the first black pixel of the hashtag is found, set the minimum x value to paint pixels black a bit forward
            if min_placement_x == 0:
                min_placement_x = i % x + x * 0.159
            # Paint the pixels black only if they are located after the hashtag
            elif i % x >= min_placement_x:
                new_img_data.append(color_black)
            else:
                new_img_data.append(color_white)
        else:
            new_img_data.append(color_white)

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_img_data)
    return new_img
