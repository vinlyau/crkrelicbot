import easyocr
import os
import time
from pprint import pprint

from .game_capture import capture_window, crop_to_donors, crop_to_relic_name
from .image_utils import process_image_for_ocr


CRK_WINDOW_NAME = 'CookieRun: Kingdom'
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')

reader = easyocr.Reader(['en'])


def process_one_capture(img_dir: str):
    # Take one screen capture
    full_filepath = os.path.join(img_dir, 'full.png')
    capture_window(CRK_WINDOW_NAME, full_filepath)

    # Crop out relic name and donors list
    relic_name_filepath = crop_to_relic_name(full_filepath)
    donors_filepath = crop_to_donors(full_filepath)

    # Pre-process images to improve OCR quality
    process_image_for_ocr(relic_name_filepath, invert=True, threshold=150, dilate=False)
    process_image_for_ocr(donors_filepath)

    # Run OCR on processed images
    # TODO: pprints to be removed
    relic_name = reader.readtext(relic_name_filepath, detail=0)
    pprint(relic_name)
    donors_list = reader.readtext(donors_filepath, detail=0)
    pprint(donors_list)

    # TODO: Add extracted info to sheet/other data storage


def run():
    run_img_dir = os.path.join(IMAGES_DIR, time.strftime("%Y_%m_%d_%H_%M_%S"))
    if not os.path.isdir(run_img_dir):
        os.makedirs(run_img_dir)

    process_one_capture(run_img_dir)


if __name__ == '__main__':
    run()
