import easyocr
import os
import time

from .game_capture import capture_window, crop_to_donors
from .image_utils import process_image_for_ocr


CRK_WINDOW_NAME = 'CookieRun: Kingdom'
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')

reader = easyocr.Reader(['en'])


def process_one_capture(img_dir: str):
    # Take one screen capture
    full_filepath = os.path.join(img_dir, 'full.png')
    capture_window(CRK_WINDOW_NAME, full_filepath)

    # Crop out everything besides the donors list
    donors_filepath = crop_to_donors(full_filepath)

    # Pre-process image to improve OCR quality
    process_image_for_ocr(donors_filepath)

    # Run OCR on processed image
    text = reader.readtext(donors_filepath, detail=0)
    print(text)


def run():
    run_img_dir = os.path.join(IMAGES_DIR, time.strftime("%Y_%m_%d_%H_%M_%S"))
    if not os.path.isdir(run_img_dir):
        os.makedirs(run_img_dir)

    process_one_capture(run_img_dir)


if __name__ == '__main__':
    run()
