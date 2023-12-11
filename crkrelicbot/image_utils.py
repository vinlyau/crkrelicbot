import cv2
import numpy as np
import os
from PIL import Image


def crop_to_region(filepath: str, region_name: str,
                   left_percent: float,
                   top_percent: float,
                   right_percent: float,
                   bot_percent: float) -> str:
    with Image.open(filepath) as img:
        width, height = img.size
        left = int(width * left_percent)
        top = int(height * top_percent)
        right = int(width * right_percent)
        bot = int(height * bot_percent)

        img = img.crop((left, top, right, bot))

        new_filepath = os.path.join(os.path.dirname(filepath), f'{region_name}.png')
        img.save(new_filepath)
        return new_filepath


def crop_to_donors(filepath: str) -> str:
    return crop_to_region(filepath, 'donors', .585, .27, .81, .58)


def crop_to_qtys(filepath: str) -> str:
    return crop_to_region(filepath, 'qtys', .81, .27, .86, .58)


def crop_to_relic_name(filepath: str) -> str:
    return crop_to_region(filepath, 'relic_name', .13, .19, .52, .28)


def binarize_image(img: np.ndarray, threshold: int) -> np.ndarray:
    _, img_thresholded = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return img_thresholded


def dilate_image(img: np.ndarray) -> np.ndarray:
    return cv2.dilate(img, cv2.getGaussianKernel(3, 1))


def invert_image(img: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(img)


def process_image_for_ocr(filepath: str,
                          binarize: bool=True,
                          invert: bool=False,
                          dilate: bool=True,
                          threshold: int=125):
    with Image.open(filepath) as img:
        img_gray = img.convert('L')
        img_arr = np.asarray(img_gray)

        if binarize:
            img_arr = binarize_image(img_arr, threshold)
        if invert:
            img_arr = invert_image(img_arr)
        if dilate:
            img_arr = dilate_image(img_arr)

        img_processed = Image.fromarray(img_arr)
        img_processed.save(filepath)
