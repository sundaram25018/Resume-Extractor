from flask import Blueprint, jsonify
from database import get_db_connection

candidate_bp = Blueprint("candidate_bp", __name__)

@candidate_bp.route("/candidates", methods=["GET"])
def get_candidates():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, phone, match_score FROM resumes ORDER BY match_score DESC")
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([{"email": email, "phone": phone, "match_score": score} for email, phone, score in candidates])
    return jsonify({"error": "Database connection failed"}), 500
