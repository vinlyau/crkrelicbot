import cv2
import numpy as np
from PIL import Image


def binarize_image(img: np.ndarray) -> np.ndarray:
    _, img_thresholded = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)
    return img_thresholded


def dilate_image(img: np.ndarray) -> np.ndarray:
    return cv2.dilate(img, cv2.getGaussianKernel(3, 1), iterations=1)


def process_image_for_ocr(filepath: str):
    with Image.open(filepath) as img:
        img_gray = img.convert('L')
        img_arr = np.asarray(img_gray)

        img_arr = binarize_image(img_arr)
        img_arr = dilate_image(img_arr)

        img_processed = Image.fromarray(img_arr)
        img_processed.save(filepath)
