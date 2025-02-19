# Resume Information Extractor

## 📌 Project Overview
This project is a **Resume Information Extractor** built using **Streamlit** and **Natural Language Processing (NLP)**. The application allows users to upload resumes in various formats (PDF, DOCX, TXT, PNG, JPG) and extracts key details such as:
- **Name**
- **Email**
- **Phone Number**

## 🚀 Features
- Supports **multiple file formats** (PDF, DOCX, TXT, PNG, JPG, JPEG)
- Uses **spaCy NLP** for **name extraction**
- Utilizes **regular expressions (regex)** for **email and phone number extraction**
- **Simple and clean UI** built with **Streamlit**
- **Fast and lightweight** resume parsing

## 🛠️ Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/sundaram25018/resume-extractor.git
cd resume-extractor
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```
> Ensure that you have Python installed (Recommended: Python 3.8+).

### **3️⃣ Run the Application**
```bash
streamlit run index.py
```
The app will start in your browser at **http://localhost:8501**.

## 📂 File Structure
```
resume-extractor/
│── index.py               # Main application script
│── requirements.txt     # Required dependencies
│── README.md            # Project documentation
```

## 🔹 Technologies Used
- **Python**
- **Streamlit** (Web UI)
- **spaCy** (NLP for Name Extraction)
- **PyMuPDF (fitz)** (PDF text extraction)
- **Regex** (Email & Phone Extraction)
- **PIL** (For text extraction from Images)

## 📜 License
This project is open-source and available under the **MIT License**.

## 🙌 Contributing
Feel free to fork this repository, submit issues, and create pull requests to improve this project!

## 📧 Contact
If you have any questions or suggestions, feel free to reach out:
- **Email**: your-email@example.com
- **GitHub**: [yourusername](https://github.com/sundaram25018)
- **LinkedIn**: [yourprofile](https://linkedin.com/in/sundaram25018)

---
### 🌟 If you found this project helpful, give it a ⭐ on GitHub!

