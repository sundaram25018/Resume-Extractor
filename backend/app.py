# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # handle cross-origin requests
import re
import fitz  # PyMuPDF
import docx
import pytesseract
from rapidfuzz import process
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if needed

model = SentenceTransformer("all-mpnet-base-v2")
nlp = spacy.load("en_core_web_sm")

# Database Connection
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sundaram@25018",
            database="resume_screening"
        )
    except mysql.connector.Error as e:
        print(f"Database Connection Error: {e}")
        return None

# --- Resume Processing Functions (same as in your Streamlit app, but adapted for Flask) ---
def extract_text_from_resume(file):
    try:
        file_type = file.content_type
        if file_type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "\n".join([page.get_text("text") for page in doc])
        elif file_type in ["image/png", "image/jpeg"]:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif file_type == "text/plain":
            text = file.read().decode("utf-8")
        else:
            text = "Unsupported file type"
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_contact_details(text):
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"

def extract_name(text):
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
    return "Not found"

SKILLS_LIST = {"HTML", "CSS", "JavaScript", "ReactJS", "VueJS", "Angular", "mongodb", "Node.js"}

def extract_skills(text):
    words = text.split()
    skills_found = [process.extractOne(word, SKILLS_LIST)[0] for word in words if process.extractOne(word, SKILLS_LIST)[1] > 80]
    return ", ".join(set(skills_found))

def extract_education_experience(text):
    doc = nlp(text)
    education, experience = [], []
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"] and any(keyword in ent.text.lower() for keyword in ["university", "college", "institute"]):
            education.append(ent.text)
        elif ent.label_ == "DATE" and any(keyword in ent.text for keyword in ["years", "months"]):
            experience.append(ent.text)
    return ", ".join(set(education)), ", ".join(set(experience))

def match_resume(resume_text, job_description):
    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding)
        return similarity_score.item()
    except Exception:
        vectorizer = TfidfVectorizer()
        docs = [resume_text, job_description]
        tfidf_matrix = vectorizer.fit_transform(docs)
        similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
        return similarity_score[0][0]

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
            print(f"Database Error: {e}")

# --- API Endpoints ---
@app.route('/upload', methods=['POST'])
def upload_resume():
    try:
        resume_file = request.files['resume']
        job_description = request.form['job_description']

        if not resume_file:
            return jsonify({'error': 'No resume file provided'}), 400

        resume_text = extract_text_from_resume(resume_file)
        if not resume_text:
            return jsonify({'error': 'Could not extract text from resume'}), 500

        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_contact_details(resume_text)
        skills = extract_skills(resume_text)
        education, experience = extract_education_experience(resume_text)
        match_score = match_resume(resume_text, job_description)

        insert_resume_data(name, email, phone, skills, experience, education, match_score)

        return jsonify({
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'education': education,
            'experience': experience,
            'match_score': match_score
        })
    except Exception as e:
        print(f"Error processing resume: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/candidates', methods=['GET'])
def get_ranked_candidates():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, match_score FROM resumes ORDER BY match_score DESC")
            candidates = cursor.fetchall()
            conn.close()
            candidate_list = [{'name': c[0], 'email': c[1], 'match_score': c[2]} for c in candidates]
            return jsonify(candidate_list)
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Database connection failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run Flask app on port 5000
