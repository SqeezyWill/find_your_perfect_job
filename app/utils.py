import os
import docx2txt
import fitz  # PyMuPDF
import string
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(docx_path):
    try:
        return docx2txt.process(docx_path)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def clean_text(text):
    text = text.lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words]
    return " ".join(tokens)

def compare_cv_to_job(cv_text, job_description):
    cleaned_cv = clean_text(cv_text)
    cleaned_job = clean_text(job_description)

    vectorizer = TfidfVectorizer(ngram_range=(1, 3))  # Capture keywords and key phrases
    tfidf_matrix = vectorizer.fit_transform([cleaned_cv, cleaned_job])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)

def generate_cv_improvement_feedback(cv_text, job_description):
    feedback = []

    # Define key sections and metrics to look for
    job_lines = job_description.strip().split("\n")
    missing_phrases = []

    for line in job_lines:
        phrase = line.strip()
        if len(phrase) > 20 and phrase.lower() not in cv_text.lower():
            missing_phrases.append(phrase)

    # Construct improved feedback section with structured advice
    if missing_phrases:
        feedback.append("📈 How to Revise & Strengthen Your CV")

        # Summary advice
        feedback.append("\n**Professional Summary**\nConsider adding a concise overview like:")
        feedback.append("“Debt‑management professional with 3+ years in credit & collections, skilled in default resolution, portfolio monitoring, and legal escalations.”")

        # Quantified Experience examples
        feedback.append("\n**Quantified Achievements**\nAdd achievements like:")
        feedback.append("• “Monitored 150+ credit accounts daily; reduced delinquency by 12%.”")
        feedback.append("• “Recovered KES 2M from defaulted clients via direct engagement.”")
        feedback.append("• “Prepared weekly MIS reports driving policy adjustments.”")
        feedback.append("• “Collaborated with legal team, initiated 20+ litigation cases.”")

        # Tools and skills
        feedback.append("\n**Skills & Tools**\nInclude:")
        feedback.append("• MS Excel (pivot tables, VLOOKUP), Credit Analysis Software")
        feedback.append("• Communication, Negotiation, Legal Liaison")

        # Education/Certifications
        feedback.append("\n**Education & Certifications**\nVerify that these are clearly listed:")
        feedback.append("• Bachelor's in Finance/Commerce/Accounting")
        feedback.append("• Certifications like Credit Risk, NACM, etc.")

        # ATS keyword alignment
        feedback.append("\n**Tailored Keywords**\nMake sure to include terms such as:")
        feedback.append("• delinquency, MIS, collections targets, write‑offs, litigation, etc.")

    return feedback
