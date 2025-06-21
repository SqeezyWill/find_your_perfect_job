import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import numpy as np
import json
import os

nlp = spacy.load("en_core_web_sm")

FEEDBACK_STORE = "feedback_scores.json"

def load_feedback():
    if os.path.exists(FEEDBACK_STORE):
        with open(FEEDBACK_STORE, "r") as f:
            return json.load(f)
    return {}

def save_feedback(data):
    with open(FEEDBACK_STORE, "w") as f:
        json.dump(data, f)

def update_feedback(job_title, cv_text, job_description, actual_score):
    key = job_title.lower().strip()
    feedback = load_feedback()
    feedback[key] = feedback.get(key, []) + [(cv_text, job_description, actual_score)]
    save_feedback(feedback)

def adjusted_weights(job_title):
    key = job_title.lower().strip()
    feedback = load_feedback()
    if key in feedback and len(feedback[key]) >= 3:
        samples = feedback[key][-3:]
        diffs = [abs(actual - calculate_match_score(cv, jd)) for cv, jd, actual in samples]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 20:
            return 0.3, 0.3, 0.4  # Emphasize keyword overlap
    return 0.4, 0.3, 0.3  # Default weights

def calculate_match_score(cv_text, job_description, job_title=""):
    cv_doc = nlp(cv_text.lower())
    jd_doc = nlp(job_description.lower())

    cv_tokens = " ".join([token.lemma_ for token in cv_doc if not token.is_stop and not token.is_punct])
    jd_tokens = " ".join([token.lemma_ for token in jd_doc if not token.is_stop and not token.is_punct])

    tfidf = TfidfVectorizer(ngram_range=(1, 3))
    vectors = tfidf.fit_transform([cv_tokens, jd_tokens])
    tfidf_similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    def extract_keywords(text):
        doc = nlp(text)
        return set([token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop])

    cv_keywords = extract_keywords(cv_text)
    jd_keywords = extract_keywords(job_description)
    overlap = cv_keywords & jd_keywords
    keyword_overlap = len(overlap) / max(len(jd_keywords), 1)

    def get_doc_vector(text):
        doc = nlp(text)
        return np.mean([token.vector for token in doc if token.has_vector], axis=0)

    try:
        cv_vector = get_doc_vector(cv_text)
        jd_vector = get_doc_vector(job_description)
        semantic_similarity = cosine_similarity([cv_vector], [jd_vector])[0][0]
    except:
        semantic_similarity = 0.0

    w_tfidf, w_semantic, w_keywords = adjusted_weights(job_title)

    rerank_score = (
        w_tfidf * tfidf_similarity +
        w_semantic * semantic_similarity +
        w_keywords * keyword_overlap
    )
    final_score = round(rerank_score * 100, 2)
    return final_score

def recommend_roles(cv_text, job_description):
    doc = nlp(cv_text.lower() + " " + job_description.lower())
    terms = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

    # Expanded known job roles
    role_terms = [
        "manager", "analyst", "officer", "specialist", "coordinator", "consultant", "lead",
        "supervisor", "administrator", "engineer", "architect", "strategist", "planner",
        "executive", "director", "developer", "representative", "advisor", "associate",
        "scientist", "auditor", "trainer", "controller", "accountant", "marketer",
        "assistant", "intern", "technician", "agent", "clerk", "recruiter", "facilitator",
        "partner", "liaison", "expert", "advisor", "caseworker", "inspector", "broker",
        "programmer", "data scientist", "product owner", "project manager", "business analyst"
    ]

    suggested_roles = []
    for phrase in terms:
        if any(role in phrase for role in role_terms):
            suggested_roles.append(phrase.title())

    if not suggested_roles:
        suggested_roles = [
            "Relevant Specialist Role", "Team Lead", "Coordinator", "Associate",
            "Consultant", "Assistant Manager", "Operations Officer", "Account Manager",
            "Program Officer", "Senior Analyst"
        ]

    return list(set(suggested_roles))

def generate_explanation(cv_text, job_description):
    cv_keywords = set([token.lemma_ for token in nlp(cv_text.lower()) if token.pos_ in ("NOUN", "PROPN")])
    jd_keywords = set([token.lemma_ for token in nlp(job_description.lower()) if token.pos_ in ("NOUN", "PROPN")])

    matched = sorted(list(cv_keywords & jd_keywords))
    missing = sorted(list(jd_keywords - cv_keywords))
    high_impact = [kw for kw in matched if len(kw) > 4]

    explanation = """
    🔍 <b>Match Explainability</b><br>
    <b>Matched Keywords:</b> {}<br>
    <b>Missing Keywords:</b> {}<br>
    <b>High Impact Phrases:</b> {}<br>
    """.format(
        ", ".join(matched[:10]) or "None",
        ", ".join(missing[:10]) or "None",
        ", ".join(high_impact[:5]) or "None"
    )

    return explanation
