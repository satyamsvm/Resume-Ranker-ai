"""Step 5 & 6 - hybrid scoring algorithm and ranking.

final = 0.45*skills + 0.30*tf-idf similarity + 0.15*experience + 0.10*education
Every component is 0-1, so the final score is shown as a percentage.
Experience is scaled by skill relevance (full credit once >=50% of JD skills match).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import config
from .features import (
    EDU_NAMES, education_level, estimate_experience_years, extract_email,
    extract_phone, guess_name, required_years,
)
from .preprocess import clean_text
from .skills import extract_skills


@dataclass
class Candidate:
    filename: str
    name: str
    email: str
    phone: str
    score: float = 0.0
    rank: int = 0
    skill_score: float = 0.0
    similarity_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    experience_years: float = 0.0
    education: str = ""
    matched_skills: list = field(default_factory=list)
    missing_skills: list = field(default_factory=list)
    extra_skills: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _skill_score(jd_skills: list[str], cand_skills: list[str]) -> float:
    if not jd_skills:
        return 0.0
    return len(set(jd_skills) & set(cand_skills)) / len(jd_skills)


def _experience_score(cand_years: float, req_years: float) -> float:
    if req_years > 0:
        return min(1.0, cand_years / req_years)
    return min(1.0, cand_years / 3.0)          # JD silent -> 3 yrs counts as "full"


def _education_score(cand_level: int, req_level: int) -> float:
    if req_level == 0:
        return 1.0 if cand_level > 0 else 0.5
    return min(1.0, cand_level / req_level)


def rank_resumes(jd_text: str, resumes: dict[str, str]) -> list[Candidate]:
    """`resumes` maps filename -> raw text. Returns candidates sorted best-first."""
    if not resumes:
        return []

    jd_skills = extract_skills(jd_text)
    req_years = required_years(jd_text)
    req_edu = education_level(jd_text)

    names = list(resumes)
    cleaned = [clean_text(resumes[n]) for n in names]
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    matrix = vec.fit_transform([clean_text(jd_text), *cleaned])
    sims = cosine_similarity(matrix[0], matrix[1:]).ravel()

    w = config.WEIGHTS
    results: list[Candidate] = []
    for fname, sim in zip(names, sims):
        text = resumes[fname]
        c_skills = extract_skills(text)
        years = estimate_experience_years(text)
        edu = education_level(text)

        skill_score = _skill_score(jd_skills, c_skills)
        # Years of experience only count as much as the skills match the job:
        # 9 years of Java should not outrank a fresher for an ML role.
        relevance = min(1.0, skill_score / 0.5) if jd_skills else 1.0

        cand = Candidate(
            filename=fname,
            name=guess_name(text, fallback=fname.rsplit(".", 1)[0]),
            email=extract_email(text),
            phone=extract_phone(text),
            skill_score=skill_score,
            similarity_score=min(1.0, float(sim) / config.TFIDF_SATURATION),
            experience_score=_experience_score(years, req_years) * relevance,
            education_score=_education_score(edu, req_edu),
            experience_years=years,
            education=EDU_NAMES[edu],
            matched_skills=sorted(set(jd_skills) & set(c_skills)),
            missing_skills=sorted(set(jd_skills) - set(c_skills)),
            extra_skills=sorted(set(c_skills) - set(jd_skills)),
        )
        cand.score = round(100 * (
            w["skills"] * cand.skill_score
            + w["similarity"] * cand.similarity_score
            + w["experience"] * cand.experience_score
            + w["education"] * cand.education_score
        ), 1)
        results.append(cand)

    results.sort(key=lambda c: (-c.score, c.name.lower()))
    for i, c in enumerate(results, 1):
        c.rank = i
    return results


def jd_summary(jd_text: str) -> dict:
    return {
        "skills": extract_skills(jd_text),
        "required_years": required_years(jd_text),
        "required_education": EDU_NAMES[education_level(jd_text)],
    }
