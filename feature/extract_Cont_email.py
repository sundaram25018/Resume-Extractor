import re 

def exctract_email(text):
  email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" 
  email = re.findall(email_pattern, text)
  if email:
    return email[0]
  else:
    return "Not found"
  

def exctract_Phone(text):
  phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  
  Phone = re.findall(phone_pattern, text)
  if Phone:
    return Phone[0]
  else:
    return "Not found"
  
text = text = '''SAMIR PANDEY
 +91-9712272260 |sameer121@gmail.com | LinkedIn| GitHub 
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
emails = exctract_email(text)
phone = exctract_Phone(text)
print("Email : " + emails)
print("Phone : " + phone)