# Interview prep - ResumeRank AI

## 30-second pitch
"I built a web app that ranks resumes against a job description. It extracts text from PDF/DOCX, cleans it with spaCy, and gives each candidate a 0-100 score from four signals: skill match, TF-IDF cosine similarity, experience and education. It also shows matched and missing skills so the ranking is explainable. It has a Flask UI, a JSON API, PDF/CSV reports, tests and Docker."

## Questions you will be asked about THIS project
**Why not only TF-IDF?** TF-IDF captures word overlap but not requirements. A resume can share many words with a JD and still miss a must-have skill. So I combine it with an explicit skill match, experience and education.

**What is TF-IDF?** Term frequency x inverse document frequency: words frequent in one document but rare across documents get high weight. I use unigrams + bigrams and `sublinear_tf` (log scaling) so repeated words do not dominate.

**What is cosine similarity?** Angle between two vectors; 1 = same direction, 0 = nothing in common. Length-independent, so a long resume is not favoured.

**Why spaCy?** Lemmatisation (running -> run) and stop-word removal reduce noise. I kept a regex fallback so the app still works without the model.

**How do you extract skills?** An editable taxonomy (`data/skills.json`) with aliases and word-boundary regex, so "java" does not match "javascript".

**How are weights chosen?** Skills 45 / similarity 30 / experience 15 / education 10 - set from domain judgement, kept in `config.py`. With recruiter feedback I would learn them (e.g. logistic regression on shortlist decisions).

**Why scale experience by skill relevance?** Without it, 9 years of Java outranked a relevant fresher for an ML role. Now experience gets full credit only when >= 50% of JD skills match.

**How do you evaluate it?** Unit tests on each component; a sample set with an expected order. For real evaluation: label resumes shortlist/reject, compute precision@k and NDCG against the ranking, compare with a TF-IDF-only baseline.

**Limitations / bias?** Taxonomy misses unknown skills, scanned PDFs need OCR, experience is year-level. Rankings can encode bias (names, gaps, college prestige) - the tool should assist a human, and an anonymised mode is on the roadmap.

**How would you scale it?** Gunicorn workers, results in Redis/PostgreSQL instead of memory, background queue (Celery) for big batches, cache TF-IDF models, add OCR service.

**Security choices?** Extension whitelist, 16 MB limit, files processed in memory (never saved), Jinja auto-escaping, CSV-injection guard.

## Topic map: PDF's Top-50 questions -> where this project shows it
| Topic | Where in the project |
|---|---|
| TF-IDF, tokenization, stemming vs lemmatization | `preprocess.py`, `scorer.py` |
| Classification vs ranking, evaluation (precision/recall/F1) | evaluation answer above |
| Feature engineering, normalization (0-1 component scores) | `features.py`, `scorer.py` |
| Saving/deploying a model as an API (Flask, Docker, CI/CD) | `routes.py`, `Dockerfile`, `ci.yml` |
| Overfitting / bias-variance (why not tune weights on 6 samples) | weights discussion |
| Word embeddings / Transformers | roadmap: sentence-transformers |

Still revise the remaining ML basics from the PDF (bagging vs boosting, CNN vs RNN, LSTM, dropout...) - interviewers go beyond the project.
