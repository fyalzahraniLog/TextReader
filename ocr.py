from PIL import ImageGrab
import pytesseract
import os

# Tesseract configuration
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text(area):
    try:
        img = ImageGrab.grab(area)
        return pytesseract.image_to_string(img, config='--oem 3 --psm 6').strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""