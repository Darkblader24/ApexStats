import re
import pytesseract
import mss
import mss.tools
from PIL import Image


def main():
    # Make a screenshot of the selected monitor
    img = make_screenshot(monitor_id=2)

    # Remove noise from screenshot
    cln_img = clean_image(img)
    # cln_img = clean_image(Image.open('data/apex_screenshot_test_half.png'))

    # Save screenshot and denoised image
    # img.save('data/apex_screenshot.png')
    cln_img.save('data/apex_stats_clean.png')

    # Detect text from denoised screenshot
    text_ocr = pytesseract.image_to_string(cln_img).lower()
    print(text_ocr)

    # Handle text data
    if 'xp breakdown' not in text_ocr:
        print('No Apex Match Summary found!')
        return

    print('\n'
          '\n'
          '\n###########################'
          '\n###### MATCH SUMMARY ######'
          '\n###########################'
          '\n')

    won_match = False
    time_survived = ''
    kills = 0
    damage_done = 0
    revives = 0
    respawns = 0
    solo = 0
    legend = 'Bang Galore'

    if 'won match' in text_ocr:
        won_match = True
    print('match won:', won_match)

    regex = re.findall('[\n\r].*time survived [(\[]*([^\n\r)\]]*)', text_ocr)
    if regex:
        time_survived = regex[0]
    else:
        print('following not found:')
    print('time survived:', time_survived)

    regex = re.findall('[\n\r].*kills [(\[]x*([^\n\r)\]]*)', text_ocr)
    if regex:
        kills = regex[0]
    else:
        print('following not found:')
    print('kills:', kills)

    regex = re.findall('[\n\r].*damage done [(\[]*([^\n\r)\]]*)', text_ocr)
    if regex:
        damage_done = regex[0]
    else:
        print('following not found:')
    print('damage done:', damage_done)

    regex = re.findall('[\n\r].*revive ally [(\[]x*([^\n\r)\]]*)', text_ocr)
    if regex:
        revives = regex[0]
    else:
        print('following not found:')
    print('revives:', revives)

    regex = re.findall('[\n\r].*respawn ally [(\[]x*([^\n\r)\]]*)', text_ocr)
    if regex:
        respawns = regex[0]
    else:
        print('following not found:')
    print('respawns:', respawns)

    regex = re.findall('[\n\r].*playing with friends [(\[]x*([^\n\r)\]]*)', text_ocr)
    if regex:
        solo = regex[0]
    else:
        print('following not found:')
    print('solo:', solo)

    regex = re.findall('[\n\r].*playing with friends [(\[]x*([^\n\r)\]]*)', text_ocr)
    if regex:
        legend = regex[0]
    else:
        print('following not found:')
    print('legend:', legend)




def clean_image(img):
    new_img_data = []

    for i, color in enumerate(img.convert('HSV').getdata()):
        h, s, v = color
        if (s <= 5 or s >= 204) and v > 127:
            new_img_data.append((0, 0, 0))
        elif s in range(56, 62) and v > 150:
            new_img_data.append((255, 0, 0))
        else:
            new_img_data.append((255, 255, 255))

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_img_data)
    return new_img


def make_screenshot(monitor_id):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]

        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", (sct_img.size[0], round(sct_img.size[1]*0.45)), sct_img.bgra, "raw", "BGRX")
    return img


if __name__ == '__main__':
    main()
