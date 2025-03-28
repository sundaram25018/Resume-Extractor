import docx2txt
import fitz
import pytesseract
from PIL import Image
import re
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_resume(file):
    text = ""
    if file.filename.endswith(".pdf"):
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    elif file.filename.endswith(".docx"):
        text = docx2txt.process(file)
    elif file.filename.endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(file)
        text = pytesseract.image_to_string(img)
    return text.strip()

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"(\+\d{1,3}[- ]?)?\d{10}", text)
    return match.group(0) if match else None
