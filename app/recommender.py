import re
import string
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    filtered = [t for t in tokens if t not in stop_words]
    return " ".join(filtered)

def recommend_most_compatible_role(cv_text, job_description, search_query):
    """
    Use a hybrid method (TF-IDF + keyword logic) to recommend most suitable role
    based on CV, job description, and searched title.
    """
    # Clean texts
    cv_clean = clean_text(cv_text)
    jd_clean = clean_text(job_description)
    role_clean = clean_text(search_query)

    combined_texts = [cv_clean, jd_clean, role_clean]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))  # Use unigrams, bigrams, and trigrams
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    # Cosine similarity
    similarity_cv_jd = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    similarity_cv_title = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[2:3])[0][0]
    similarity_jd_title = cosine_similarity(tfidf_matrix[1:2], tfidf_matrix[2:3])[0][0]

    # Combine with weights (can be tuned)
    hybrid_score = (0.5 * similarity_cv_jd) + (0.3 * similarity_cv_title) + (0.2 * similarity_jd_title)

    # Normalize to 0–100
    match_percentage = round(hybrid_score * 100, 2)

    # Hierarchical role recommendation based on similarity and current role
    role_hierarchy = [
        "Customer Service Agent",
        "Debt Collections Officer",
        "Collections Associate",
        "Debt Collections Supervisor",
        "Assistant Head - Delinquent Loan Recoveries",
        "Head of Debt Recovery",
        "Repayment Manager",
        "Head of Credit Risk and Collections",
        "Director of Credit Risk"
    ]

    # Map role title to score
    role_scores = []
    for role in role_hierarchy:
        vector = vectorizer.transform([clean_text(role)])
        score = cosine_similarity(tfidf_matrix[0:1], vector)[0][0]
        role_scores.append((role, score))

    # Get the best matched role from hierarchy
    most_compatible_role = sorted(role_scores, key=lambda x: x[1], reverse=True)[0][0]

    return most_compatible_role, match_percentage
