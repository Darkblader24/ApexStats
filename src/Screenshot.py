
from PIL import Image
import mss
import mss.tools

from src.Color import Color


class Screenshot:

    im = None

    def __init__(self, monitor_area):
        with mss.mss as sct:
            sct_img = sct.grab(monitor_area)
            self.im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return

    def save(self, filepath):
        self.im.save(filepath)
        return

    def clean(self, color_filter):
        new_img_data = []
        color_black = (0, 0, 0)
        color_white = (255, 255, 255)

        for i, colordata in enumerate(self.im.convert("HSV").getdata()):
            color = Color(colordata)
            if color in color_filter:
                new_img_data.append(color_black)
                continue
            new_img_data.append(color_white)
        return

    def read(self):
        return
