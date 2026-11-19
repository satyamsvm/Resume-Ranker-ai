"""Central configuration. Scoring weights live here so they are easy to tune."""
import os

# Final score = weighted sum of four components (weights must add up to 1.0)
WEIGHTS = {
    "skills": 0.45,       # overlap between JD skills and resume skills
    "similarity": 0.30,   # TF-IDF cosine similarity (JD vs resume text)
    "experience": 0.15,   # estimated years vs. years asked in JD
    "education": 0.10,    # highest degree vs. degree asked in JD
}

# Cosine similarity between a JD and a resume rarely goes above ~0.5,
# so we saturate it there to get a 0-1 score that is easier to read.
TFIDF_SATURATION = 0.50

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_UPLOAD_MB = 16
MAX_RESUMES = 50
RESULT_CACHE_SIZE = 50

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
