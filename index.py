import streamlit as st
import fitz  # PyMuPDF
import re
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text):
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not found"

def extract_name(text):
    # Extract top 5 lines (names are typically at the start)
    lines = text.split("\n")[:10]  

    # Step 1: Look for a full name pattern (two capitalized words)
    for line in lines:
        words = line.strip().split()
        print(words)
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

def extract_links(text):
    linkedin_pattern = r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-_/]+"
    github_pattern = r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-_/]+"

    linkedin_links = re.findall(linkedin_pattern, text)
    github_links = re.findall(github_pattern, text)

    linkedin = linkedin_links[0][0] if linkedin_links else "Not found"
    github = github_links[0][0] if github_links else "Not found"

    return linkedin, github

def extract_hyperlinks_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    links = []

    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                links.append(link["uri"])

    return links

def main():
    st.title("Resume Information Extractor")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        # linkedin, github = extract_links(text)
        # pdf_links = extract_hyperlinks_from_pdf(uploaded_file)


        # for link in pdf_links:
        #    if "linkedin.com/in" in link:
        #     linkedin = link
        #    elif "github.com" in link:
        #     github = link
        
      
        
        st.subheader("Extracted Information")
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone:** {phone}")
        # st.write(f"**LinkedIn:** {linkedin}")
        # st.write(f"**GitHub:** {github}")
        
        

if __name__ == "__main__":
    main()
