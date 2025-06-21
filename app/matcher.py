from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils import clean_text, normalize_skills, boolean_weighted_score, extract_skills
import numpy as np
# If available, you can import word/embed models, e.g., from sentence_transformers

# Optional placeholder for real embedding model
def embed_text(text):
    # Replace with real embedding, e.g. SentenceTransformer.encode()
    return np.mean(TfidfVectorizer().fit_transform([text]).toarray(), axis=0)

def compute_hybrid_score(cv_text, jd_text, jd_skills, skill_weights, alpha=0.5):
    cv_tok = clean_text(cv_text)
    jd_tok = clean_text(jd_text)
    cv_norm = " ".join(cv_tok)
    jd_norm = " ".join(jd_tok)

    # Boolean + weighted skill match
    bool_score, weight_score = boolean_weighted_score(cv_tok, jd_tok, jd_skills, skill_weights)

    # Semantic similarity using embeddings
    emb_cv = embed_text(cv_norm)
    emb_jd = embed_text(jd_norm)
    sem_score = float(cosine_similarity([emb_cv], [emb_jd])[0][0])

    # Phrase-level similarity via n‑gram TF‑IDF
    vect = TfidfVectorizer(ngram_range=(1,4))
    tfidf = vect.fit_transform([cv_norm, jd_norm])
    phrase_score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])

    # Combine all signals, alpha controls semantic contribution
    hybrid = alpha * sem_score + (1 - alpha) * (phrase_score*0.7 + bool_score*0.3)
    return round(hybrid * 100, 2), {
       'boolean': bool_score * 100,
       'weighted': weight_score,
       'semantic': sem_score * 100,
       'phrase': phrase_score * 100
    }

def compare_cv_to_job(cv_text, jd_text):
    jd_tok = clean_text(jd_text)
    skills = extract_skills(jd_tok)
    weights = {s: 1.0 for s in skills}  # simple uniform weights; can refine later
    score, components = compute_hybrid_score(cv_text, jd_text, skills, weights)
    return score, components
