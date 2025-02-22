import spacy

nlp = spacy.load("en_core_web_sm")

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


text = '''SAMIR PANDEY
 +91-9712272260 | ✉️pandeysameer121@gmail.com | LinkedIn| GitHub 
EDUCATION
Bachelor of Technology in Computer Science and Engineering (Big Data Analytics)
Parul University, Vadodara Sept 2021-Jul 2025
Higher Secondary Certificate Examination
Doon International Public School, Ahmedabad Apr 2020-May 2021
SKILLS
• Programming: Python (NumPy, Pandas, Matplotlib, Seaborn, SciPy, Scikit-learn), SQL
• Data Science: Machine Learning, Data Cleaning, Statistical Analysis, Data Visualization, Web Scraping
• Tools: MS Excel, Google Analytics, Tableau, Power BI
• Soft Skills: Problem-Solving, Teamwork, Communication, Adaptability, Attention to Detail, Critical 
Thinking, Time Management

'''
name = extract_name(text)
print("Name : " + name)

