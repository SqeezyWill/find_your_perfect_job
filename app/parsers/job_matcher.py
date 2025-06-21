from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_jobs(cv_text, job_description):
    """
    Compare CV text with a job description using TF-IDF + Cosine Similarity.
    Returns a score between 0 and 1.
    """
    documents = [cv_text, job_description]
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return score

def generate_recommendation(score):
    """
    Return a simple recommendation based on score.
    """
    if score > 0.75:
        return "Excellent match – Highly Recommended"
    elif score > 0.5:
        return "Good match – Worth Applying"
    elif score > 0.3:
        return "Moderate match – Consider Improving Your CV"
    else:
        return "Low match – Not Recommended"
