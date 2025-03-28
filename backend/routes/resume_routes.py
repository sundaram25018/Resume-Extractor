from flask import Blueprint, request, jsonify
from services.resume_processing import extract_text_from_resume, extract_email, extract_phone
from services.matching import match_resume
from database import get_db_connection

resume_bp = Blueprint("resume_bp", __name__)

@resume_bp.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files or "job_description" not in request.form:
        return jsonify({"error": "Missing file or job description"}), 400

    file = request.files["resume"]
    job_description = request.form["job_description"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    resume_text = extract_text_from_resume(file)
    if resume_text:
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        match_score = match_resume(resume_text, job_description)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO resumes (email, phone, match_score) VALUES (%s, %s, %s)",
            (email, phone, match_score),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "email": email, "phone": phone, "match_score": match_score
        })
    return jsonify({"error": "Failed to extract text from resume"}), 500
