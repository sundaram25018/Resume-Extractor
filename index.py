import streamlit as st
import re
import docx2txt
import fitz  # PyMuPDF for PDFs
import mysql.connector
from mysql.connector import pooling, Error
import spacy
from PIL import Image
import pytesseract
from rapidfuzz import process
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import cv2
import numpy as np

# Configure Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Initialize NLP Model
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-mpnet-base-v2")

# Precompile regex patterns
PHONE_PATTERN = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Database Connection Pool
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sundaram@25018",
    "database": "resume_screening"
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

# Get database connection
def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Optimized text extraction
def extract_text_from_resume(uploaded_file):
    try:
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            return "\n".join(page.get_text("text") for page in doc)
        
        elif file_type.startswith("image"):
            image = Image.open(uploaded_file)
            image = image.convert("L")  # Convert to grayscale
            return pytesseract.image_to_string(image)
        
        elif file_type.endswith("document"):
            return docx2txt.process(uploaded_file)
        
        elif file_type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        
        return "Unsupported file type"
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None

# Optimized contact details extraction
def extract_contact_details(text):
    phones = PHONE_PATTERN.findall(text)
    return phones[0] if phones else "Not found"

def extract_email(text):
    emails = EMAIL_PATTERN.findall(text)
    return emails[0] if emails else "Not found"

# Improved name extraction
def extract_name(text):
    doc = nlp(text[:500])  # Limit analysis to first 500 characters
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not found"

# Extract education & experience
def extract_education_experience(text):
    doc = nlp(text)
    education = set()
    experience = set()
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"] and "university" in ent.text.lower():
            education.add(ent.text)
        elif ent.label_ == "DATE" and any(kw in ent.text for kw in ["years", "months"]):
            experience.add(ent.text)
    return ", ".join(education), ", ".join(experience)

# Parallelized resume-job matching using embeddings
def match_resume(resume_text, job_description):
    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        return util.pytorch_cos_sim(resume_embedding, job_embedding).item()
    except Exception:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

# Insert extracted data into MySQL
def insert_resume_data(name, email, phone, skills, experience, education, match_score):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM resumes WHERE email = %s", (email,))
            if cursor.fetchone():
                st.warning(f"⚠️ Resume for {email} already exists!")
                return
            sql = """INSERT INTO resumes (name, email, phone, skills, experience, education, match_score) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, email, phone, skills, experience, education, match_score))
            conn.commit()
            st.success(f"✅ Resume for {name} added successfully!")
        except Error as e:
            st.error(f"Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

# Streamlit UI
st.set_page_config(page_title="AI-Powered Resume Screening", layout="wide")
st.title("\U0001F4C4 AI-Powered Resume Screening System")

uploaded_file = st.file_uploader("\U0001F4C2 Upload Resume", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
job_description = st.text_area("\U0001F4DD Enter Job Description")

if uploaded_file and job_description:
    resume_text = extract_text_from_resume(uploaded_file)
    if resume_text:
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_contact_details(resume_text)
        education, experience = extract_education_experience(resume_text)
        match_score = match_resume(resume_text, job_description)
        insert_resume_data(name, email, phone, '', experience, education, match_score)

        st.markdown(f"""
        ### 🔍 Extracted Details
        - **👤 Name:** {name}
        - **📧 Email:** {email}
        - **📱 Phone:** {phone}
        - **🎓 Education:** {education}
        - **📈 Experience:** {experience}
        - **✅ Match Score:** {match_score:.2f}
        """, unsafe_allow_html=True)

# Show ranked candidates
st.subheader("\U0001F3C6 Ranked Candidates")
