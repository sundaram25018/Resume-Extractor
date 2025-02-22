import streamlit as st
import re
import docx2txt
import fitz  # PyMuPDF for PDFs
import mysql.connector
import spacy
from rapidfuzz import process
from sentence_transformers import SentenceTransformer, util

# Load AI model for semantic matching
model = SentenceTransformer("all-MiniLM-L6-v2")
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
    file_type = uploaded_file.name.split(".")[-1]
    if file_type == "pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc]).strip()
    elif file_type == "docx":
        return docx2txt.process(uploaded_file)
    return None

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
SKILLS_LIST = {"Python", "Machine Learning", "Deep Learning", "Data Science", "NLP", "MySQL", "TensorFlow", "Keras"}

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
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding)
    return similarity_score.item()

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
st.title("\U0001F4C4 AI-Powered Resume Screening System")

uploaded_file = st.file_uploader("\U0001F4C2 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
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
