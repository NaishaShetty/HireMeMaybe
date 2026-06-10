from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env before any module that reads env vars
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Structured logging + Sentry — must be set up before any logger.getLogger() calls
from app.logging_config import setup_logging
setup_logging()

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.ats.ats_scorer import calculate_ats_score
from app.cover_letter.cover_letter_engine import CoverLetterEngine
from app.data.rewrite_dataset import append_rewrite_example
from app.intelligence.company_engine import CompanyIntelEngine
from app.interview.interview_engine import InterviewEngine
from app.matcher.match_engine import match_resume_to_jd
from app.parsers.contact_parser import extract_email, extract_phone
from app.parsers.resume_text_extractor import extract_pdf_text
from app.parsers.section_parser import extract_sections
from app.parsers.skill_parser import extract_skills
import time as _time
from app.utils.text_utils import sanitize_for_prompt
from app.database import init_db, log_request
from app.rewrite.diff_analyzer import DiffAnalyzer
from app.rewrite.hallucination_guard import HallucinationGuard
from app.rewrite.optimization_loop import OptimizationLoop
from app.rewrite.recommendation_engine import RecommendationEngine
from app.rewrite.resume_formatter import export_resume, export_cover_letter_pdf
from app.rewrite.rewrite_analyzer import RewriteAnalyzer
from app.rewrite.rewrite_engine import RewriteEngine
from app.rewrite.rewrite_evaluator import RewriteEvaluator
from app.parsers.jd_image_parser import JDImageParserError, extract_jd_from_image
from app.parsers.jd_url_parser import JDURLParserError, extract_jd_from_url
from app.services.jd_builder import build_jd_json
from app.services.resume_builder import build_resume_json
from app.similarity.similarity_engine import calculate_similarity

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="HireMeMaybe API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

REWRITE_ENGINE = RewriteEngine()
INTERVIEW_ENGINE = InterviewEngine()
COMPANY_INTEL_ENGINE = CompanyIntelEngine()
REWRITE_EVALUATOR = RewriteEvaluator()
COVER_LETTER_ENGINE = CoverLetterEngine()

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup() -> None:
    init_db()
    logger.info("HireMeMaybe API started")


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start = _time.monotonic()
    response = None
    error_detail = None
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        error_detail = str(exc)
        raise
    finally:
        latency_ms = round((_time.monotonic() - start) * 1000, 2)
        status_code = response.status_code if response else 500
        client_ip = request.client.host if request.client else None

        log_request(
            endpoint=request.url.path,
            method=request.method,
            client_ip=client_ip,
            status_code=status_code,
            latency_ms=latency_ms,
            error=error_detail,
        )

        log_fn = logger.error if status_code >= 500 else logger.warning if status_code >= 400 else logger.info
        log_fn(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "client_ip": client_ip,
                "error": error_detail,
            },
        )

_ALLOWED_EXTENSIONS = {".pdf"}


class JDRequest(BaseModel):
    text: str


class JDURLRequest(BaseModel):
    url: str = Field(..., description="Public URL of a job posting")


class MatchRequest(BaseModel):
    resume: dict[str, Any]
    jd: dict[str, Any]


class SimilarityRequest(BaseModel):
    resume_text: str
    jd_text: str


class RewriteResumeRequest(BaseModel):
    resume: dict[str, Any]
    jd: dict[str, Any]
    resume_text: str
    jd_text: str
    max_passes: int = Field(default=1, ge=1, le=3)
    num_candidates: int = Field(default=3, ge=1, le=5)


class ExportResumeRequest(BaseModel):
    resume_text: str
    format: str = Field(default="pdf", pattern="^(pdf|docx)$")


class InterviewScoreRequest(BaseModel):
    resume: dict[str, Any]
    jd: dict[str, Any]
    resume_text: str
    jd_text: str


class EvaluateRewriteRequest(BaseModel):
    original_text: str
    rewritten_text: str
    rewritten_resume: dict[str, Any]
    jd: dict[str, Any]
    resume_text: str
    jd_text: str


class InterviewPrepRequest(BaseModel):
    resume_text: str
    jd_text: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class CompanyIntelRequest(BaseModel):
    company: str
    role: str = Field(default="Software Engineer")


class CoverLetterRequest(BaseModel):
    resume_text: str
    jd_text: str
    role: str = Field(default="the role")
    company: str = Field(default="your company")


class ExportCoverLetterRequest(BaseModel):
    cover_letter: str
    company: str = Field(default="")


def _build_analysis(*, ats_score, semantic_score, missing_skills, matched_skills, skill_match_score):
    analysis = RewriteAnalyzer.analyze(
        ats_score=ats_score,
        semantic_score=semantic_score,
        missing_skills=missing_skills,
    )
    analysis.update({
        "ats_score": round(float(ats_score), 2),
        "semantic_score": round(float(semantic_score), 4),
        "skill_match_score": round(float(skill_match_score), 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    })
    return analysis


def _calculate_interview_probability(ats_score, semantic_score, skill_match_score):
    semantic_pct = semantic_score * 100
    base = ats_score * 0.35 + semantic_pct * 0.30 + skill_match_score * 0.25
    if ats_score >= 75 and semantic_pct >= 75 and skill_match_score >= 75:
        base += 5.0
    return round(min(100.0, max(0.0, base)), 2)


def _build_interview_insights(ats_score, semantic_score, skill_match_score, matched_skills, missing_skills, interview_probability):
    strengths, weaknesses, risk_factors, recommendations = [], [], [], []

    if ats_score >= 75:
        strengths.append("Strong ATS keyword alignment")
    if semantic_score >= 0.75:
        strengths.append("High semantic relevance to the job description")
    if skill_match_score >= 75:
        strengths.append("Good coverage of required technical skills")
    if matched_skills:
        top = matched_skills[:5]
        strengths.append(f"Matched {len(matched_skills)} required skill(s): {', '.join(top)}")

    if ats_score < 60:
        weaknesses.append("Low ATS score — resume may not pass automated screening")
    elif ats_score < 75:
        weaknesses.append("Moderate ATS score — room to improve keyword coverage")
    if semantic_score < 0.60:
        weaknesses.append("Low semantic similarity — resume may not feel relevant to the role")
    elif semantic_score < 0.75:
        weaknesses.append("Moderate semantic relevance — consider emphasising aligned experience")
    if skill_match_score < 50:
        weaknesses.append("Significant skill gap — fewer than half the required skills are present")
    if missing_skills:
        top_missing = missing_skills[:5]
        weaknesses.append(f"Missing {len(missing_skills)} required skill(s): {', '.join(top_missing)}")

    if interview_probability < 40:
        risk_factors.append("High risk of rejection at ATS stage")
    if len(missing_skills) > 5:
        risk_factors.append("Large number of missing skills may disqualify the application")
    if ats_score < 50:
        risk_factors.append("Resume is unlikely to reach a human recruiter without optimisation")

    if ats_score < 75:
        recommendations.append("Increase keyword density by naturally integrating job description terms")
    if semantic_score < 0.75:
        recommendations.append("Reframe experience descriptions to mirror the language in the job posting")
    for skill in missing_skills[:3]:
        recommendations.append(f"Mention '{skill}' if you have genuine experience with it")
    if not strengths:
        recommendations.append("Consider a resume rewrite to improve alignment with this role")
        strengths.append("Application submitted — optimisation recommended before applying")

    return {"strengths": strengths, "weaknesses": weaknesses, "risk_factors": risk_factors, "recommendations": recommendations}


@app.get("/")
def root():
    return {"message": "HireMeMaybe API Running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "HireMeMaybe"}


@app.post("/parse-resume")
@limiter.limit("30/minute")
async def parse_resume(request: Request, file: UploadFile = File(...)):
    safe_name = Path(file.filename or "upload").name
    if Path(safe_name).suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are supported. Got: '{Path(safe_name).suffix or 'no extension'}'",
        )
    file_path = UPLOAD_DIR / safe_name
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        text = extract_pdf_text(str(file_path))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}") from exc
    finally:
        # Always delete the uploaded file — resumes contain PII.
        try:
            file_path.unlink(missing_ok=True)
        except Exception as del_exc:
            logger.warning("Failed to delete uploaded file %s: %s", file_path, del_exc)
    safe_text = sanitize_for_prompt(text)
    email = extract_email(safe_text)
    phone = extract_phone(safe_text)
    skills = extract_skills(safe_text)
    sections = extract_sections(safe_text)
    return {**build_resume_json(email=email, phone=phone, skills=skills, sections=sections), "resume_text": safe_text}


@app.post("/parse-jd")
@limiter.limit("30/minute")
async def parse_jd(request: Request, jd: JDRequest):
    if not jd.text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    safe_text = sanitize_for_prompt(jd.text)
    return build_jd_json(safe_text)


@app.post("/parse-jd-from-url")
@limiter.limit("20/minute")
async def parse_jd_from_url(request: Request, body: JDURLRequest):
    """Extract and parse a job description from a public URL.

    Tries direct HTTP scraping first; falls back to Jina AI Reader for
    JavaScript-rendered pages (LinkedIn, Workday, etc.).
    """
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    try:
        raw_text = extract_jd_from_url(url)
    except JDURLParserError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"URL fetch failed: {exc}") from exc
    safe_text = sanitize_for_prompt(raw_text)
    if not safe_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the provided URL.")
    return {**build_jd_json(safe_text), "raw_text": safe_text}


_ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
_EXTENSION_TO_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


@app.post("/parse-jd-from-image")
@limiter.limit("10/minute")
async def parse_jd_from_image(request: Request, file: UploadFile = File(...)):
    """Extract and parse a job description from a screenshot of a job posting.

    Accepts PNG, JPG, WEBP, or GIF. Uses vision LLM (OpenAI / Gemini / Anthropic)
    to OCR the image and extract structured JD data.
    """
    ext = Path(file.filename or "upload").suffix.lower()
    if ext not in _ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload a PNG, JPG, WEBP, or GIF screenshot.",
        )
    mime_type = _EXTENSION_TO_MIME[ext]
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        raw_text = extract_jd_from_image(image_bytes, mime_type=mime_type)
    except JDImageParserError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image OCR failed: {exc}") from exc
    safe_text = sanitize_for_prompt(raw_text)
    if not safe_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the image.")
    return {**build_jd_json(safe_text), "raw_text": safe_text}


@app.post("/match-resume-jd")
@limiter.limit("30/minute")
async def match_resume_jd(request: Request, body: MatchRequest):
    match_result = match_resume_to_jd(body.resume, body.jd)
    ats_score = calculate_ats_score(body.resume, body.jd, match_result)
    return {
        "ats_score": ats_score,
        "skill_match_score": match_result["skill_match_score"],
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
    }


@app.post("/semantic-match")
@limiter.limit("30/minute")
async def semantic_match(request: Request, body: SimilarityRequest):
    similarity = calculate_similarity(
        sanitize_for_prompt(body.resume_text),
        sanitize_for_prompt(body.jd_text),
    )
    return {"semantic_similarity": similarity}


@app.post("/interview-score")
@limiter.limit("20/minute")
async def interview_score(request: Request, body: InterviewScoreRequest):
    match_result = match_resume_to_jd(body.resume, body.jd)
    ats_score = calculate_ats_score(body.resume, body.jd, match_result)
    semantic_score = calculate_similarity(body.resume_text, body.jd_text)
    skill_match_score = match_result["skill_match_score"]
    matched_skills = match_result["matched_skills"]
    missing_skills = match_result["missing_skills"]
    interview_probability = _calculate_interview_probability(
        ats_score=ats_score, semantic_score=semantic_score, skill_match_score=skill_match_score,
    )
    insights = _build_interview_insights(
        ats_score=ats_score, semantic_score=semantic_score, skill_match_score=skill_match_score,
        matched_skills=matched_skills, missing_skills=missing_skills, interview_probability=interview_probability,
    )
    return {
        "interview_probability_score": interview_probability,
        "ats_score": round(ats_score, 2),
        "semantic_similarity": round(float(semantic_score), 4),
        "skill_match_score": round(skill_match_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        **insights,
    }


@app.post("/rewrite-resume")
@limiter.limit("10/minute")
async def rewrite_resume(request: Request, body: RewriteResumeRequest):
    safe_resume_text = sanitize_for_prompt(body.resume_text)
    safe_jd_text = sanitize_for_prompt(body.jd_text)
    match_result = match_resume_to_jd(body.resume, body.jd)
    before_score = calculate_ats_score(body.resume, body.jd, match_result)
    semantic_score = calculate_similarity(safe_resume_text, safe_jd_text)
    analysis = _build_analysis(
        ats_score=before_score, semantic_score=semantic_score,
        missing_skills=match_result["missing_skills"],
        matched_skills=match_result["matched_skills"],
        skill_match_score=match_result["skill_match_score"],
    )
    recommendations = RecommendationEngine.generate(analysis)
    optimizer = OptimizationLoop(
        max_passes=body.max_passes,
        num_candidates=body.num_candidates,
        rewrite_engine=REWRITE_ENGINE,
    )
    optimization = optimizer.optimize(
        resume=body.resume, jd=body.jd,
        resume_text=safe_resume_text, jd_text=safe_jd_text,
        recommendations=recommendations["recommendations"],
    )
    changes = DiffAnalyzer.analyze(
        before=safe_resume_text, after=optimization["optimized_resume"],
    )["changes"]
    hallucination_report = HallucinationGuard().verify(
        safe_resume_text, optimization["optimized_resume"], jd_text=safe_jd_text,
    ).to_dict()
    if optimization["accepted"]:
        try:
            append_rewrite_example(
                resume_before=body.resume_text,
                resume_after=optimization["optimized_resume"],
                jd=body.jd_text,
                ats_before=optimization["before_score"],
                ats_after=optimization["after_score"],
                improvement=optimization["improvement"],
            )
        except Exception as exc:
            logger.warning("Dataset logging failed: %s", exc)
    return {
        "before_score": optimization["before_score"],
        "after_score": optimization["after_score"],
        "improvement": optimization["improvement"],
        "accepted": optimization["accepted"],
        "candidate_resume": optimization["candidate_resume"],
        "attempts": optimization["attempts"],
        "analysis": analysis,
        "recommendations": recommendations,
        "changes": changes,
        "optimized_resume": optimization["optimized_resume"],
        "evaluation": optimization.get("evaluation", {}),
        "hallucination_report": hallucination_report,
    }



@app.post("/interview-prep")
@limiter.limit("10/minute")
async def interview_prep(request: Request, body: InterviewPrepRequest):
    """Generate interview questions, weakness probes, and STAR answer drafts."""
    result = INTERVIEW_ENGINE.generate(
        resume_text=sanitize_for_prompt(body.resume_text),
        jd_text=sanitize_for_prompt(body.jd_text),
        matched_skills=body.matched_skills,
        missing_skills=body.missing_skills,
    )
    return result.to_dict()


@app.post("/company-intel")
@limiter.limit("10/minute")
async def company_intel(request: Request, body: CompanyIntelRequest):
    """Generate a company intelligence report for interview preparation."""
    if not body.company.strip():
        raise HTTPException(status_code=400, detail="Company name cannot be empty.")
    result = COMPANY_INTEL_ENGINE.generate(
        company=sanitize_for_prompt(body.company),
        role=sanitize_for_prompt(body.role),
    )
    return result.to_dict()


@app.post("/generate-cover-letter")
@limiter.limit("10/minute")
async def generate_cover_letter(request: Request, body: CoverLetterRequest):
    """Generate a tailored cover letter from a resume and job description."""
    if not body.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    if not body.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    result = COVER_LETTER_ENGINE.generate(
        resume_text=sanitize_for_prompt(body.resume_text),
        jd_text=sanitize_for_prompt(body.jd_text),
        role=body.role,
        company=body.company,
    )
    return result.to_dict()


@app.post("/export-resume")
@limiter.limit("20/minute")
async def export_resume_endpoint(request: Request, body: ExportResumeRequest):
    """Export a plain-text resume as PDF or DOCX."""
    if not body.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    try:
        file_bytes, media_type, filename = export_resume(body.resume_text, body.format)
    except Exception as exc:
        logger.error("export_resume failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}") from exc
    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/export-cover-letter-pdf")
@limiter.limit("20/minute")
async def export_cover_letter_pdf_endpoint(request: Request, body: ExportCoverLetterRequest):
    """Render a plain-text cover letter as a PDF."""
    if not body.cover_letter.strip():
        raise HTTPException(status_code=400, detail="Cover letter text cannot be empty.")
    try:
        file_bytes = export_cover_letter_pdf(body.cover_letter, company=body.company)
    except Exception as exc:
        logger.error("export_cover_letter_pdf failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}") from exc
    safe_company = re.sub(r"[^a-zA-Z0-9_\- ]", "", body.company).strip().replace(" ", "_")
    filename = f"Cover_Letter_{safe_company}.pdf" if safe_company else "Cover_Letter.pdf"
    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
