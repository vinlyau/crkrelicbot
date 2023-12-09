import mss.tools
import time
import pyautogui
import pytesseract
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/ASUS/Desktop/crk/guild/crkguild-a603e1e75609.json', scope)
client = gspread.authorize(creds)
sheet = client.open('ChromaticHaze Dmg/Relic Sheet')
worksheet = sheet.worksheet('Relics')
column_index = 1
column_values = worksheet.col_values(column_index)

def check(y):
    pyautogui.click(550, y)
    with mss.mss() as sct:
        relic = {
            "top": 370,
            "left" : 1050,
            "width": 115,
            "height": 35
        }
        name = {
            "top": 167,
            "left" : 850,
            "width": 275,
            "height": 40
        }
        relic_photo = sct.grab(relic)
        mss.tools.to_png(relic_photo.rgb, relic_photo.size, output="relic.screenshot.png")
        name_photo = sct.grab(name)
        mss.tools.to_png(name_photo.rgb, name_photo.size, output="name.screenshot.png")

        name_img = Image.open('name.screenshot.png')
        name_text = pytesseract.image_to_string(name_img)

        relic_img = Image.open('relic.screenshot.png')
        relic_text = pytesseract.image_to_string(relic_img)

        cell_index = None
        for index, value in enumerate(column_values):
            if value == name_text.strip():
                cell_index = index + 1
                break

        # EACH WEEK INCREASE THE COLOMN INDEX!
        if cell_index is not None:
            worksheet.update_cell(cell_index, column_index + 3, relic_text)
        else:
            print(f"There's no {name_text}")

        time.sleep(0.2)

        pyautogui.click(550, 250)
        start_x, start_y = 550, 250
        end_x, end_y = 550, 121.5
        drag_duration = 0.25
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=drag_duration)
        pyautogui.mouseUp()

time.sleep(1)

for i in range(25):
    check(250)
for i in range(5):
    a = i * 130
    b = 250 + a
    check(b)
