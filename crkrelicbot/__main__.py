import easyocr
import os
import shutil
import time
from pprint import pprint
from string import ascii_lowercase, ascii_uppercase, punctuation, whitespace

from .game_capture import capture_window, crop_to_donors, crop_to_qtys, crop_to_relic_name
from .image_utils import process_image_for_ocr


# -- Script-required metadata --
CRK_WINDOW_NAME = 'CookieRun: Kingdom'
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')

# -- Useful Macros --
KNAME_BLOCKLIST = f'{punctuation}{whitespace}'
RNAME_ALLOWLIST = f'{ascii_lowercase}{ascii_uppercase}\'-&: '
RQTYS_ALLOWLIST = 'x0123456789'

# -- Globals --
# easyocr reader only needs to be initialized once per language combination
reader = easyocr.Reader(['en'])


def process_one_capture(img_dir: str):
    # Take one screen capture
    full_filepath = os.path.join(img_dir, 'full.png')
    capture_window(CRK_WINDOW_NAME, full_filepath)

    # Crop out relic name and donors list
    relic_name_filepath = crop_to_relic_name(full_filepath)
    donors_filepath = crop_to_donors(full_filepath)
    qtys_filepath = crop_to_qtys(full_filepath)

    # Pre-process images to improve OCR quality
    process_image_for_ocr(relic_name_filepath, invert=True, threshold=150, dilate=False)
    process_image_for_ocr(donors_filepath)
    process_image_for_ocr(qtys_filepath, threshold=100)

    # Run OCR on processed images
    # TODO: pprints to be removed
    relic_name = reader.readtext(relic_name_filepath, allowlist=RNAME_ALLOWLIST, paragraph=True)
    pprint(relic_name)
    donors_list = reader.readtext(donors_filepath, blocklist=KNAME_BLOCKLIST)
    pprint(donors_list)
    qtys_list = reader.readtext(qtys_filepath, allowlist=RQTYS_ALLOWLIST)
    pprint(qtys_list)

    # TODO: Add extracted info to sheet/other data storage


def run():
    run_img_dir = os.path.join(IMAGES_DIR, time.strftime("%Y_%m_%d_%H_%M_%S"))
    if not os.path.isdir(run_img_dir):
        os.makedirs(run_img_dir)

    # TODO: change this to a function that will run for all relics/pages
    #       currently left as-is for testing purposes only
    process_one_capture(run_img_dir)

    # Duplicate the images in a 'latest' directory for convenience
    # TODO: Add ability to specify CL arg to disable this feature
    latest_img_dir = os.path.join(IMAGES_DIR, 'latest')
    shutil.copytree(run_img_dir, latest_img_dir, dirs_exist_ok=True)


if __name__ == '__main__':
    run()
