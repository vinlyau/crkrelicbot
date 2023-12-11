import easyocr
import os
import shutil
import time
from pprint import pprint
from string import ascii_lowercase, ascii_uppercase, punctuation, whitespace

from . import window
from .image_utils import process_image_for_ocr, crop_to_donors, crop_to_qtys, crop_to_relic_name


# -- Script-required metadata --
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')

# -- Useful Macros --
KNAME_BLOCKLIST = f'{punctuation}{whitespace}'
RNAME_ALLOWLIST = f'{ascii_lowercase}{ascii_uppercase}\'-&: '
RQTYS_ALLOWLIST = 'x0123456789'
OCR_BBOX_IDX = 0
OCR_TEXT_IDX = 1
OCR_CONF_IDX = 2

# -- Globals --
# easyocr reader only needs to be initialized once per language combination
reader = easyocr.Reader(['en'])


# Processes a single screenshot of a Relic Details page
def process_one_capture(img_dir: str, first_capture: bool=False):
    # Take one screen capture
    full_filepath = os.path.join(img_dir, 'full.png')
    window.capture(full_filepath)

    # Crop out relic name and donors list
    relic_name_filepath = crop_to_relic_name(full_filepath)
    donors_filepath = crop_to_donors(full_filepath)
    qtys_filepath = crop_to_qtys(full_filepath)

    # Pre-process images to improve OCR quality
    process_image_for_ocr(relic_name_filepath, invert=True, threshold=150, dilate=False)
    process_image_for_ocr(donors_filepath)
    process_image_for_ocr(qtys_filepath, threshold=100)

    # Run OCR on processed images
    # TODO: prints/pprints to be removed
    relic_name = reader.readtext(relic_name_filepath, allowlist=RNAME_ALLOWLIST, paragraph=True)
    pprint(relic_name)
    donors_list = reader.readtext(donors_filepath, blocklist=KNAME_BLOCKLIST)
    pprint(donors_list)
    qtys_list = reader.readtext(qtys_filepath, allowlist=RQTYS_ALLOWLIST)
    pprint(qtys_list)

    # On first capture only, if the first QTY detected has low confidence
    # then scroll a tiny bit down in order to skip the 'First Donor' row
    if first_capture:
        if qtys_list[0][OCR_CONF_IDX] < 0.95:
            print('Most likely detected the "Donor" string in qtys list')
            window.scroll_one_relic_row(full_filepath)
            process_one_capture(img_dir)

    return full_filepath


# Processes multiple screenshots covering the relic's entire Donors list
def process_relic(img_dir: str):
    # Process the first screenshot - there are special rules applicable here
    full_filepath = process_one_capture(img_dir, first_capture=True)

    # TODO: fix below to intelligently determine when Donors list is complete
    # Loop until entire Donors list has been processed
    window.scroll_one_relic_page(full_filepath)

    # At end of processing current relic, click to next relic
    # window.click_to_next_relic(full_filepath) # TODO: uncomment this line


def run():
    run_img_dir = os.path.join(IMAGES_DIR, time.strftime("%Y_%m_%d_%H_%M_%S"))
    if not os.path.isdir(run_img_dir):
        os.makedirs(run_img_dir)

    # TODO: change this to a function that will run for all relics/pages
    #       currently left as-is for testing purposes only
    process_relic(run_img_dir)

    # Duplicate the images in a 'latest' directory for convenience
    # TODO: Add ability to specify CL arg to disable this feature
    latest_img_dir = os.path.join(IMAGES_DIR, 'latest')
    shutil.copytree(run_img_dir, latest_img_dir, dirs_exist_ok=True)


if __name__ == '__main__':
    window.prepare()
    run()
    window.cleanup()
