# ResumeRank AI
![CI](https://github.com/satyamsvm/Resume-Ranker-ai/actions/workflows/ci.yml/badge.svg)

Rank a stack of resumes against a job description and get a shortlist **with reasons** (matched skills, missing skills, score breakdown). Built with Flask, scikit-learn and spaCy.

> Internship project (Elevate Labs, AI/ML) - "AI-Powered Resume Ranker", improved with a hybrid scoring model, a JSON API, tests, CI and Docker so it can grow into a real product.

## Features

* Upload **PDF, DOCX or TXT** resumes (up to 50 at once) and paste or upload a job description
* **Hybrid score (0-100)** - not just keyword counting:

|Component|Weight|How it is computed|
|-|-|-|
|Skills|45%|share of JD skills found in the resume (editable taxonomy in `data/skills.json`)|
|Text similarity|30%|TF-IDF (1-2 grams) cosine similarity between JD and resume|
|Experience|15%|estimated years (date ranges + "N years") vs. years asked; scaled by skill relevance|
|Education|10%|highest degree found vs. degree asked|

* Explainable results: matched / missing skills and a stacked score bar per candidate
* Contact details (email, phone) and name extracted automatically
* **Download HR report** as PDF or CSV
* **JSON API** (`POST /api/rank`) for integrating with other tools
* Dark mode, keyboard accessible, mobile friendly

## Quick start

```bash
git clone https://github.com/<satyamsvm>/resume-ranker-ai.git
cd resume-ranker-ai
python -m venv .venv \&\& source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m spacy download en\_core\_web\_sm                # optional but recommended
python run.py                                          # http://127.0.0.1:5000
```

Try it with `data/sample\_job\_description.txt` and the files in `data/sample\_resumes/`.

spaCy is optional: if the model is not installed the app automatically uses a lightweight regex pipeline (`/health` shows which engine is active).

## API example

```bash
curl -F "job\_description=<data/sample\_job\_description.txt" \\
     -F "resumes=@data/sample\_resumes/aarav\_mehta.pdf" \\
     -F "resumes=@data/sample\_resumes/priya\_nair.txt" \\
     http://127.0.0.1:5000/api/rank
```

## Project structure

```
app/
  extractor.py    PDF/DOCX/TXT -> text
  preprocess.py   cleaning, lemmatisation (spaCy) + fallback
  skills.py       skill extraction from data/skills.json
  features.py     email, phone, name, experience years, education
  scorer.py       hybrid scoring + ranking  <- the core algorithm
  report.py       PDF / CSV reports
  routes.py       web pages + JSON API
  config.py       weights and limits
tests/            unit + web tests (python -m unittest discover -s tests)
data/             skills taxonomy, sample JD and resumes
docs/             project report (PDF) and interview prep
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Deploy / launch

* **Docker:** `docker build -t resumerank . \&\& docker run -p 8000:8000 resumerank`
* **Render:** push to GitHub -> New Web Service -> it reads `render.yaml`
* **Any PaaS:** uses `Procfile` (`gunicorn run:app`). Set `SECRET\_KEY` as an environment variable.

## Known limitations

* Skill matching is taxonomy-based: skills not in `data/skills.json` are invisible (add more!).
* Scanned (image-only) PDFs need OCR first.
* Experience is estimated from years/date ranges at year granularity.
* Results are kept in memory (last 50 runs) - fine for one server, use Redis/DB for scale.
* Rankings assist a recruiter; they should not be the only basis for a hiring decision.

## Roadmap (towards a real product)

1. Sentence-embedding similarity (e.g. `sentence-transformers`) alongside TF-IDF
2. OCR for scanned resumes (Tesseract)
3. User accounts + saved job posts (PostgreSQL), Redis for results
4. Bias-reduction: optional anonymised mode hiding name/gender signals
5. Recruiter feedback loop to learn better weights
6. Stripe billing for a hosted SaaS

## License

MIT

