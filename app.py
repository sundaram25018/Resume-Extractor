import streamlit as st
import re
import docx2txt
import fitz  # PyMuPDF for PDFs
import mysql.connector
import spacy
from PIL import Image
import docx
import pytesseract
from rapidfuzz import process
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Load AI model for semantic matching
model = SentenceTransformer("all-mpnet-base-v2")
nlp = spacy.load("en_core_web_sm")

# Database connection
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sundaram@25018",
            database="resume_screening"
        )
    except mysql.connector.Error as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Extract text from resume
def extract_text_from_resume(uploaded_file):
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

# Extract contact details
# def extract_contact_details(text):
#     email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
#     phone_pattern = r"\\+?\\d{10,13}"
    
#     email = re.findall(email_pattern, text)
#     phone = re.findall(phone_pattern, text)
    
#     return email[0] if email else None, phone[0] if phone else None

def extract_contact_details(text):
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

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


# Extract skills using fuzzy matching
SKILLS_LIST = {"HTML", "CSS", "JavaScript", "ReactJS", "VueJS", "Angular", "mongodb", "Node.js"}

def extract_skills(text):
    words = text.split()
    skills_found = [process.extractOne(word, SKILLS_LIST)[0] for word in words if process.extractOne(word, SKILLS_LIST)[1] > 80]
    return ", ".join(set(skills_found))

# Extract education & experience using spaCy
def extract_education_experience(text):
    doc = nlp(text)
    education, experience = [], []
    
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"] and any(keyword in ent.text.lower() for keyword in ["university", "college", "institute"]):
            education.append(ent.text)
        elif ent.label_ == "DATE" and any(keyword in ent.text for keyword in ["years", "months"]):
            experience.append(ent.text)
    
    return ", ".join(set(education)), ", ".join(set(experience))

# Match resume with job description
def match_resume(resume_text, job_description):
    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding)
        return similarity_score.item()
    
    except Exception:
        # Fallback to TF-IDF
        vectorizer = TfidfVectorizer()
        docs = [resume_text, job_description]
        tfidf_matrix = vectorizer.fit_transform(docs)
        similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
        return similarity_score[0][0]

# Insert extracted data into MySQL
def insert_resume_data(name, email, phone, skills, experience, education, match_score):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            sql = """INSERT INTO resumes (name, email, phone, skills, experience, education, match_score) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, email, phone, skills, experience, education, match_score))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            st.error(f"Database Error: {e}")

# Streamlit UI
st.set_page_config(page_title="AI-Powered Resume Screening", layout="wide")
st.markdown("""
    <style>
        .stTextInput, .stTextArea {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton>button {
            background-color: black;
            color: black;
            border-radius: 10px;
            padding: 10px;
        }
        .main {
            background-color: black;
        }
    </style>
""", unsafe_allow_html=True)
st.title("\U0001F4C4 AI-Powered Resume Screening System")

uploaded_file = st.file_uploader("\U0001F4C2 Upload Resume", type=["pdf", "docx","txt", "png", "jpg", "jpeg"])
job_description = st.text_area("\U0001F4DD Enter Job Description")

if uploaded_file and job_description:
    resume_text = extract_text_from_resume(uploaded_file)
    
    if resume_text:
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_contact_details(resume_text)
        skills = extract_skills(resume_text)
        education, experience = extract_education_experience(resume_text)
        match_score = match_resume(resume_text, job_description)

        insert_resume_data(name, email, phone, skills, experience, education, match_score)

        # Display extracted information
        
        st.subheader("\U0001F50D Extracted Details")
        st.write(f"**\U0001F464 Email:** {name}")
        st.write(f"**\U0001F4E7 Email:** {email}")
        st.write(f"**\U0001F4F1 Phone:** {phone}")
        st.write(f"**\U0001F4A1 Skills:** {skills}")
        st.write(f"**\U0001F393 Education:** {education}")
        st.write(f"**\U0001F4C8 Experience:** {experience}")
        st.write(f"**\U00002705 Match Score:** {match_score:.2f}")

# Show ranked candidates
st.subheader("\U0001F3C6 Ranked Candidates")
conn = connect_db()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, match_score FROM resumes ORDER BY match_score DESC")
    candidates = cursor.fetchall()
    conn.close()
    for idx, (c_name, c_email, c_score) in enumerate(candidates, start=1):
        st.write(f"**{idx}. {c_name}** ({c_email}) - Match Score: {c_score:.2f}")
