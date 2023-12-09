import os
import pathlib
import win32con
import win32gui
import win32ui
from ctypes import windll
from PIL import Image

# Adapted from https://stackoverflow.com/questions/7561049/what-is-the-
# difference-between-getclientrect-and-getwindowrect-in-winapi
def capture_window(window_name: str, filepath: str):
    hwnd = win32gui.FindWindow(None, window_name)

    # Get window sizing
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result == 0:
        raise Exception('Failed to PrintWindow')

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    size = (bmpinfo['bmWidth'], bmpinfo['bmHeight'])
    with Image.frombuffer('RGB', size, bmpstr, 'raw', 'BGRX', 0, 1) as img:
        img.save(filepath)


def crop_to_donors(filepath: str) -> str:
    with Image.open(filepath) as img:
        width, height = img.size
        left = int(width * .585)
        top = int(height * .27)
        right = int(width * .86)
        bot = int(height * .58)

        img = img.crop((left, top, right, bot))

        donors_filepath = os.path.join(os.path.dirname(filepath), 'donors.png')
        img.save(donors_filepath)
        return donors_filepath
