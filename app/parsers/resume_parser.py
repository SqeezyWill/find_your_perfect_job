import re
from docx import Document
import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_resume(text):
    resume_data = {
        'name': None,
        'email': None,
        'phone': None,
        'skills': [],
        'education': [],
        'experience': [],
        'certifications': []
    }

    # Extract email and phone
    email_match = re.search(r'\b[\w.-]+?@\w+?\.\w+\b', text)
    phone_match = re.search(r'\+?\d[\d\s().-]{7,}\d', text)
    if email_match:
        resume_data['email'] = email_match.group()
    if phone_match:
        resume_data['phone'] = phone_match.group()

    # Extract skills
    known_skills = ['python', 'java', 'sql', 'machine learning', 'data analysis', 'flask', 'excel', 'communication']
    resume_data['skills'] = [skill for skill in known_skills if skill.lower() in text.lower()]

    # Extract education section (simple example)
    education_section = re.findall(r'(B\.Sc|M\.Sc|Diploma|Degree|Bachelor|Master).*', text, re.IGNORECASE)
    resume_data['education'] = education_section

    # Extract experience section
    experience_section = re.findall(r'(\d+\+? years? of experience.*|worked at .*|experience in .*|responsibilities included .*\.)', text, re.IGNORECASE)
    resume_data['experience'] = experience_section

    # Extract certifications
    certifications = re.findall(r'(certified in .*|completed .* certification)', text, re.IGNORECASE)
    resume_data['certifications'] = certifications

    return resume_data
