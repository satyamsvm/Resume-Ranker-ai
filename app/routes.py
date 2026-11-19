"""Web UI + JSON API."""
from __future__ import annotations

import os
import uuid
from collections import OrderedDict

from flask import (Blueprint, Response, jsonify, render_template, request, abort)

from . import config, report
from .extractor import ExtractionError, extract_text
from .preprocess import backend_name
from .scorer import jd_summary, rank_resumes

bp = Blueprint("main", __name__)

# Tiny in-memory store so users can download reports after ranking.
# (Use Redis/DB when you scale to multiple workers - see README roadmap.)
_RESULTS: "OrderedDict[str, dict]" = OrderedDict()


def _remember(payload: dict) -> str:
    rid = uuid.uuid4().hex[:12]
    _RESULTS[rid] = payload
    while len(_RESULTS) > config.RESULT_CACHE_SIZE:
        _RESULTS.popitem(last=False)
    return rid


def _read_inputs():
    """Validate the request and return (jd_text, {filename: text}, errors)."""
    jd_text = (request.form.get("job_description") or "").strip()
    jd_file = request.files.get("jd_file")
    if not jd_text and jd_file and jd_file.filename:
        try:
            jd_text = extract_text(jd_file.filename, jd_file.read())
        except ExtractionError as exc:
            return "", {}, [str(exc)]

    errors, resumes = [], {}
    files = [f for f in request.files.getlist("resumes") if f and f.filename]
    if len(jd_text) < 30:
        errors.append("Please paste a job description (at least a couple of lines).")
    if not files:
        errors.append("Please upload at least one resume (PDF, DOCX or TXT).")
    if len(files) > config.MAX_RESUMES:
        errors.append(f"Maximum {config.MAX_RESUMES} resumes per run.")
        files = files[:config.MAX_RESUMES]

    for f in files:
        name = os.path.basename(f.filename)
        if os.path.splitext(name)[1].lower() not in config.ALLOWED_EXTENSIONS:
            errors.append(f"{name}: unsupported type (use PDF, DOCX or TXT).")
            continue
        try:
            resumes[name] = extract_text(name, f.read())
        except ExtractionError as exc:
            errors.append(str(exc))
    if not resumes and not errors:
        errors.append("No readable resumes found.")
    return jd_text, resumes, errors


@bp.get("/")
def index():
    return render_template("index.html", backend=backend_name())


@bp.post("/rank")
def rank():
    jd_text, resumes, errors = _read_inputs()
    if not resumes:
        return render_template("index.html", errors=errors, backend=backend_name()), 400

    candidates = [c.to_dict() for c in rank_resumes(jd_text, resumes)]
    title = (request.form.get("job_title") or "").strip()[:120]
    jd = jd_summary(jd_text)
    rid = _remember({"candidates": candidates, "title": title, "jd": jd})
    return render_template("results.html", candidates=candidates, title=title,
                           jd=jd, rid=rid, warnings=errors)


@bp.post("/api/rank")
def api_rank():
    """JSON API: multipart form with job_description + resumes[]."""
    jd_text, resumes, errors = _read_inputs()
    if not resumes:
        return jsonify({"error": errors}), 400
    candidates = [c.to_dict() for c in rank_resumes(jd_text, resumes)]
    return jsonify({"job": jd_summary(jd_text), "candidates": candidates, "warnings": errors})


@bp.get("/download/<rid>.<fmt>")
def download(rid: str, fmt: str):
    data = _RESULTS.get(rid)
    if data is None or fmt not in ("csv", "pdf"):
        abort(404)
    if fmt == "csv":
        body, mime = report.to_csv(data["candidates"]), "text/csv"
    else:
        body = report.to_pdf(data["candidates"], data["title"], data["jd"])
        mime = "application/pdf"
    return Response(body, mimetype=mime, headers={
        "Content-Disposition": f"attachment; filename=resume_ranking.{fmt}"})


@bp.get("/health")
def health():
    return jsonify(status="ok", nlp_backend=backend_name())
