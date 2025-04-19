from PIL import ImageGrab
import pytesseract
import os
import time

TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text(area):
    try:
        img = ImageGrab.grab(area)
        text = pytesseract.image_to_string(img, config='--oem 3 --psm 6').strip()
        return text
    except Exception as e:
        print(f"[OCR Error] {e}")
        return ""
