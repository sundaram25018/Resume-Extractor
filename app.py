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

# Configure Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize NLP Model
nlp = spacy.load("en_core_web_sm")

# Database Connection Pool
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sundaram@25018",
    "database": "resume_screening"
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Extract text from resume
def extract_text_from_resume(uploaded_file):
    try:
        file_type = uploaded_file.type

        if file_type == "application/pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                return "\n".join(page.get_text("text") for page in doc)

        elif file_type in ["image/png", "image/jpeg"]:
            return pytesseract.image_to_string(Image.open(uploaded_file))

        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(uploaded_file)  # Faster extraction

        elif file_type == "text/plain":
            return uploaded_file.read().decode("utf-8")

        return "Unsupported file type"
    
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None

# Extract contact details
def extract_contact_details(text):
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

# Extract name
def extract_name(text):
    try:
        lines = text.split("\n")[:10]  

        for line in lines:
            words = line.strip().split()
            if len(words) == 2 and all(w.isalpha() and w[0].isupper() for w in words):
                return line.strip()

        for line in lines:
            if line.isupper() and "RESUME" not in line and "CURRICULUM" not in line:
                return line.strip()
        
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

    except Exception as e:
        st.error(f"Error extracting name: {e}")

    return "Not found"
# Extract education & experience
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
def extract_skills_from_resume(resume_text, job_description):
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        documents = [job_description, resume_text]  # Compare job description with resume

        tfidf_matrix = vectorizer.fit_transform(documents)
        job_keywords = set(vectorizer.get_feature_names_out())  # Extract job-related words

        resume_words = set(resume_text.lower().split())  # Convert resume text to words
        matched_skills = job_keywords & resume_words  # Find common words

        return ", ".join(matched_skills) if matched_skills else "No relevant skills found"

    except Exception as e:
        st.error(f"Error extracting skills: {e}")
        return "Error in skill extraction"

# Match resume with job description
def match_resume(resume_text, job_description):
    try:
        model = SentenceTransformer("all-mpnet-base-v2")  
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)

        if resume_embedding.shape == job_embedding.shape:  
            return util.pytorch_cos_sim(resume_embedding, job_embedding).item()

    except Exception:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

# Insert extracted data into MySQL with duplicate handling
def insert_resume_data(name, email, phone, skills, experience, education, match_score):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT email FROM resumes WHERE email = %s", (email,))
            if cursor.fetchone():
                st.warning(f"⚠️ Resume for {email} already exists in the database!")
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

# Function to delete a resume from the database with confirmation
def delete_resume(email):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes WHERE email = %s", (email,))
            conn.commit()
            st.success(f"🗑️ Resume for {email} deleted successfully!")
        except Error as e:
            st.error(f"Error deleting resume: {e}")
        finally:
            cursor.close()
            conn.close()
            st.experimental_rerun()

# Streamlit UI
st.set_page_config(page_title="AI-Powered Resume Screening", layout="wide")

st.title("\U0001F4C4 AI-Powered Resume Screening System")

uploaded_file = st.file_uploader("\U0001F4C2 Upload Resume", type=["pdf", "docx","txt", "png", "jpg", "jpeg"])
job_description = st.text_area("\U0001F4DD Enter Job Description")

if uploaded_file and job_description:
    resume_text = extract_text_from_resume(uploaded_file)
    
    if resume_text:
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_contact_details(resume_text)
        skills = extract_skills_from_resume(resume_text, job_description)
        education,experience = extract_education_experience(resume_text)
        match_score = match_resume(resume_text, job_description)

        insert_resume_data(name, email, phone, skills, experience, education, match_score)

        st.markdown(f"""
        ### 🔍 Extracted Details
        - **👤 Name:** {name}
        - **📧 Email:** {email}
        - **📱 Phone:** {phone}
        - **💡 Skills:** {skills}
        - **🎓 Education:** {education}
        - **📈 Experience:** {experience}
        - **✅ Match Score:** {match_score:.2f}
        """, unsafe_allow_html=True)

# Show ranked candidates with delete button
st.subheader("\U0001F3C6 Ranked Candidates")
conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, match_score FROM resumes ORDER BY match_score DESC")
    candidates = cursor.fetchall()
    conn.close()

    for idx, (c_name, c_email, c_score) in enumerate(candidates, start=1):
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write(f"**{idx}. {c_name}** ({c_email}) - Match Score: {c_score:.2f}")
        with col2:
            if st.button(f"❌ Delete {idx}", key=f"delete_{c_email}"):
                delete_resume(c_email)  
