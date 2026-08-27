# -*- coding: utf-8 -*-
import os
import pytesseract

TESSERACT_DIR = r"C:\Program Files\Tesseract-OCR"
path = os.path.join(TESSERACT_DIR, "tesseract.exe")

print("Файл существует:", os.path.exists(path))

# Путь для pytesseract
pytesseract.tesseract_cmd = path

# PATH только внутри этого процесса
if TESSERACT_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + TESSERACT_DIR

# Проверка версии
try:
    print("Версия tesseract:", pytesseract.get_tesseract_version())
except Exception as e:
    print("Ошибка pytesseract:", repr(e))

# Реальный тест OCR на куске экрана
try:
    import pyautogui
    img = pyautogui.screenshot(region=(0, 0, 400, 150))
    text = pytesseract.image_to_string(img)
    print("OCR работает, распознано символов:", len(text))
except Exception as e:
    print("Ошибка OCR:", repr(e))