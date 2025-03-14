# AI-Powered Resume Screening System

## Overview
This AI-powered Resume Screening System uses **Machine Learning, NLP, and Deep Learning** to analyze resumes and match them against job descriptions. The system extracts candidate details such as **name, email, phone number, skills, education, and experience**, then calculates a **match score** using **transformers and TF-IDF**. It provides a **Streamlit-based web interface** and stores the extracted data in a **MySQL database**.

## Features
- 🏆 **AI-Powered Resume Screening** using Sentence Transformers (`all-mpnet-base-v2`)
- 📂 **Supports PDF,DOCX,JPG,JPEG,PNG,TXT resumes**
- 🔍 **Extracts candidate details** (Name, Email, Phone, Skills, Education, Experience)
- 📊 **Matches resumes with job descriptions** based on semantic similarity
- 🏛 **Stores results in MySQL database**
- 🌐 **User-friendly Streamlit Web App**
- 🔄 **Fallback TF-IDF model for better accuracy**

## Technologies Used
- **Python**
- **Streamlit** (Web App UI)
- **MySQL** (Database)
- **Sentence Transformers** (for job matching)
- **TF-IDF** (fallback for similarity matching)
- **Fuzzy Matching** (for skill extraction)
- **PyMuPDF** (for PDF text extraction)
- **docx2txt** (for DOCX text extraction)
- **PIL** (for IMAGE text extraction)
- **Regular Expressions** (for email & phone extraction)

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/resume-screening.git
cd resume-screening
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
Create a MySQL database and run the following SQL command:
```sql
CREATE DATABASE resume_screening;
USE resume_screening;
CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    skills TEXT,
    experience TEXT,
    education TEXT,
    match_score FLOAT
);
```

### 4. Configure Database Credentials
Modify `config.py` (or inside `app.py`) with your MySQL details:
```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "yourpassword"
DB_NAME = "resume_screening"
```

### 5. Run the Application
```bash
streamlit run app.py
```
![image](https://github.com/user-attachments/assets/2d3fd494-df81-412a-b846-64c285a4dc4c)

## Usage
1. Upload a **PDF,JPGE,JPG,PNG,TXT,DOCX** resume.
2. Enter the **Job Description**.
3. The system extracts and displays:
   - Candidate Name 👤
   - Email 📧
   - Phone Number 📞
   - Skills 💡
   - Experience 📊
   - Education 🎓
   - Match Score ✅
4. Data is **stored in MySQL**.
5. View **Ranked Candidates** based on match score.

## Future Improvements
- 📌 **Use LLaMA or Falcon** for better name/entity extraction
- 📌 **Add a dashboard with filters & analytics**
- 📌 **Deploy using Docker & Cloud Services**

## Contributing
Feel free to **fork** this repository, **improve** the code, and **submit a pull request**! 🚀

## License
This project is licensed under the **MIT License**.

