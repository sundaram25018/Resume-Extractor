import streamlit as st
import fitz  # PyMuPDF
import re
import spacy
from PIL import Image
import pytesseract
import docx
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text("text") for page in doc])

    elif file_type in ["image/png", "image/jpeg"]:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)  # OCR for text extraction

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    else:
        return "Unsupported file type"

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text):
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"

def extract_name(text):
    # Extract top 5 lines (names are typically at the start)
    lines = text.split("\n")[:10]  

    # Step 1: Look for a full name pattern (two capitalized words)
    for line in lines:
        words = line.strip().split()
        if len(words) == 2 and all(w.isalpha() and w[0].isupper() for w in words):
            return line.strip()

    # Step 2: Look for the first non-generic capitalized line
    for line in lines:
        if line.isupper() and "RESUME" not in line and "CURRICULUM" not in line:
            return line.strip()
    
    # Step 3: Try using NLP (Fallback)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return "Not found"

def main():
    st.set_page_config(page_title="Resume Extractor", layout="wide", page_icon="📄")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    st.title("📄 Resume Information Extractor")
    if uploaded_file:
        with st.spinner("Extracting text..."):
            text = extract_text_from_file(uploaded_file)
            if text == "Unsupported file type":
                st.error("File type not supported.")
            else:
                name = extract_name(text)
                email = extract_email(text)
                phone = extract_phone(text)

        st.markdown("---") 

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("👤 Name")
            st.info(name, icon="🔍")

        with col2:
            st.subheader("📧 Email")
            st.success(email, icon="✉️")

        with col3:
            st.subheader("📞 Phone")
            st.warning(phone, icon="📱")
            
        
        

if __name__ == "__main__":
    main()
