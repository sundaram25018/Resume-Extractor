from flask import Flask
from flask_cors import CORS
from routes.resume_routes import resume_bp
from routes.candidate_routes import candidate_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(resume_bp)
app.register_blueprint(candidate_bp)

if __name__ == "__main__":
    app.run(debug=True)
