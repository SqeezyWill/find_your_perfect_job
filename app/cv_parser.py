import os
import re
import spacy
import docx
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def extract_cv_text(file_path):
    text = ""
    if file_path.lower().endswith('.pdf'):
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            print(f"Error reading PDF: {e}")
    elif file_path.lower().endswith(('.doc', '.docx')):
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")
    return text

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text.strip()) > 1:
            keywords.add(chunk.text.strip().lower())
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "ADJ") and len(token.text.strip()) > 1:
            keywords.add(token.lemma_.strip().lower())
    return list(keywords)

def generate_cv_feedback(cv_text, job_description):
    feedback_sections = []

    cv_keywords = set(extract_keywords(cv_text))
    jd_keywords = set(extract_keywords(job_description))
    missing_keywords = jd_keywords - cv_keywords

    # Section: Structural Recommendations
    structure_tips = []
    if len(cv_text.strip()) < 100:
        structure_tips.append("📌 <strong>Expand your CV:</strong> Add more detail on roles, accomplishments, and responsibilities.")

    if "education" not in cv_text.lower() and any("degree" in word or "bachelor" in word for word in jd_keywords):
        structure_tips.append("📌 <strong>Include Education:</strong> List your highest academic qualification or certifications.")

    if "experience" not in cv_text.lower() and any("years" in word or "experience" in word for word in jd_keywords):
        structure_tips.append("📌 <strong>Highlight Experience:</strong> Include roles with measurable outcomes (e.g., 'Increased collections by 23%').")

    if "skills" not in cv_text.lower() and any("skills" in word or "proficiency" in word for word in jd_keywords):
        structure_tips.append("📌 <strong>Add Skills Section:</strong> Mention both technical and soft skills relevant to the role.")

    if structure_tips:
        feedback_sections.append("<h6>📋 Resume Structure & Content</h6><ul>" + "".join([f"<li>{tip}</li>" for tip in structure_tips]) + "</ul>")

    # Section: Missing Keywords
    if missing_keywords:
        keyword_block = sorted(missing_keywords)
        keyword_list = ", ".join(keyword_block)
        feedback_sections.append(f"<h6>🧩 Tailor Keywords from Job Description</h6><p>Consider adding these missing terms to better align with the role: <em>{keyword_list}</em></p>")

    if not feedback_sections:
        feedback_sections.append("<p>✅ Your CV aligns well with the job description. Minor tweaks may help highlight strengths even more.</p>")

    return "".join(feedback_sections)
