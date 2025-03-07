import fitz
from PIL import Image
import docx
import pytesseract
import streamlit as st
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_file(uploaded_file):
  file_type = uploaded_file.type

  if file_type == "application/pdf":
    docs = fitz.open(stream = uploaded_file.read(),filetype="pdf")
    return "\n".join([page.get_text("text") for page in docs ])
  elif file_type in ["image/png", "image/jpeg"]:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)
  elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
  elif file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")
  else:
      return "Unsupported file type"
  

st.title("Text Extraction from a files")


uploaded_file = st.file_uploader("Upload files", type=["pdf", "docx","txt", "png", "jpg", "jpeg"])

files = extract_file(uploaded_file)
st.write(files)
