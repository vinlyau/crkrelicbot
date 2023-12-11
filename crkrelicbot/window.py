import pyautogui
import pywinauto
import time
import win32gui
import win32ui
from ctypes import windll
from PIL import Image


# -- Script-required metadata --
CRK_WINDOW_NAME = 'CookieRun: Kingdom'
CRK_HWND = win32gui.FindWindow(None, CRK_WINDOW_NAME)


# -- Globals --
crk_window = None


def prepare():
    global crk_window
    crk_app = pywinauto.Application()
    crk_app.connect(handle=CRK_HWND)
    crk_window = crk_app.window()
    if crk_window.is_minimized():
        raise Exception('Game window cannot be minimized prior to script run')
    crk_app.window().maximize()
    crk_app.window().set_focus()


def cleanup():
    global crk_window
    crk_window.minimize()


# Adapted from https://stackoverflow.com/questions/7561049/what-is-the-
# difference-between-getclientrect-and-getwindowrect-in-winapi
def capture(filepath: str):
    # Get window sizing
    left, top, right, bot = win32gui.GetClientRect(CRK_HWND)
    width = right - left
    height = bot - top

    hwndDC = win32gui.GetWindowDC(CRK_HWND)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(CRK_HWND, saveDC.GetSafeHdc(), 3)
    if result == 0:
        raise Exception('Failed to PrintWindow')

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(CRK_HWND, hwndDC)

    size = (bmpinfo['bmWidth'], bmpinfo['bmHeight'])
    with Image.frombuffer('RGB', size, bmpstr, 'raw', 'BGRX', 0, 1) as img:
        img.save(filepath)


def drag(full_img: str, x1: float, y1: float, x2: float, y2: float,
         duration: float=0.5, hold_s: float=0.5, grace_s: float=0.5):
    with Image.open(full_img) as img:
        width, height = img.size
        start_x = int(width * x1)
        start_y = int(height * y1)
        end_x = int(width * x2)
        end_y = int(height * y2)

    # Convert from client coordinates (e.g., relative position within game window)
    # to absolute screen coordinates for pyautogui
    start_x, start_y = win32gui.ClientToScreen(CRK_HWND, (start_x, start_y))
    end_x, end_y = win32gui.ClientToScreen(CRK_HWND, (end_x, end_y))

    pyautogui.moveTo(x=start_x, y=start_y)
    pyautogui.mouseDown()
    pyautogui.moveTo(x=end_x, y=end_y, duration=duration)
    time.sleep(hold_s) # Need to wait to nullify inertial scrolling
    pyautogui.mouseUp()
    time.sleep(grace_s) # Grace period since scrolling too far results in a scrollback


def scroll_one_relic_page(full_img: str):
    drag(full_img, .7117, .5739, .7117, .2684)


def scroll_one_relic_row(full_img: str):
    drag(full_img, .7117, .5739, .7117, .5175, duration=0.5)


def click(full_img: str, x: float, y: float):
    with Image.open(full_img) as img:
        width, height = img.size
        click_x = int(width * x)
        click_y = int(height * y)

    # Convert from client coordinates (e.g., relative pixel position in-game)
    # to absolute screen coordinates for pyautogui
    click_x, click_y = win32gui.ClientToScreen(CRK_HWND, (click_x, click_y))
    pyautogui.click(x=click_x, y=click_y, duration=0.5)


def click_to_next_relic(full_img: str):
    click(full_img, .4841, .4361)
