
from PIL import Image
import mss
import mss.tools

from src.Color import Color
import pytesseract


class Screenshot(Image):

    # im = None

    def __init__(self, monitor_area):
        with mss.mss as sct:
            sct_img = sct.grab(monitor_area)
            # self.im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            tempim = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            self.putdata(tempim.getdata())
        return

    def save(self, filepath):
        self.im.save(filepath)
        return

    def clean(self, filter_func):
        new_img_data = []
        color_black = (0, 0, 0)
        color_white = (255, 255, 255)

        for i, colordata in enumerate(self.im.convert("HSV").getdata()):
            color = Color(colordata)
            if filter_func(color):
                new_img_data.append(color_black)
                continue
            new_img_data.append(color_white)

        self.im = Image.new(self.im.mode, self.im.size)
        self.im.putdata(new_img_data)
        return

    def read(self, *args):
        return pytesseract.image_to_string(self.im, *args).lower()
