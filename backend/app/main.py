from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env before any module that reads env vars
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.ats.ats_scorer import calculate_ats_score
from app.data.rewrite_dataset import append_rewrite_example
from app.intelligence.company_engine import CompanyIntelEngine
from app.interview.interview_engine import InterviewEngine
from app.matcher.match_engine import match_resume_to_jd
from app.parsers.contact_parser import extract_email, extract_phone
from app.parsers.resume_text_extractor import extract_pdf_text
from app.parsers.section_parser import extract_sections
from app.parsers.skill_parser import extract_skills
from app.rewrite.diff_analyzer import DiffAnalyzer
from app.rewrite.optimization_loop import OptimizationLoop
from app.rewrite.recommendation_engine import RecommendationEngine
from app.rewrite.resume_formatter import export_resume
from app.rewrite.rewrite_analyzer import RewriteAnalyzer
from app.rewrite.rewrite_engine import RewriteEngine
from app.rewrite.rewrite_evaluator import RewriteEvaluator
from app.services.jd_builder import build_jd_json
from app.services.resume_builder import build_resume_json
from app.similarity.similarity_engine import calculate_similarity

app = FastAPI(title="HireMeMaybe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

REWRITE_ENGINE = RewriteEngine()
INTERVIEW_ENGINE = InterviewEngine()
COMPANY_INTEL_ENGINE = CompanyIntelEngine()
REWRITE_EVALUATOR = RewriteEvaluator()

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_ALLOWED_EXTENSIONS = {".pdf"}


class JDRequest(BaseModel):
    text: str


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
async def parse_resume(file: UploadFile = File(...)):
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
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    sections = extract_sections(text)
    return {**build_resume_json(email=email, phone=phone, skills=skills, sections=sections), "resume_text": text}


@app.post("/parse-jd")
async def parse_jd(jd: JDRequest):
    if not jd.text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    return build_jd_json(jd.text)


@app.post("/match-resume-jd")
async def match_resume_jd(request: MatchRequest):
    match_result = match_resume_to_jd(request.resume, request.jd)
    ats_score = calculate_ats_score(request.resume, request.jd, match_result)
    return {
        "ats_score": ats_score,
        "skill_match_score": match_result["skill_match_score"],
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
    }


@app.post("/semantic-match")
async def semantic_match(request: SimilarityRequest):
    similarity = calculate_similarity(request.resume_text, request.jd_text)
    return {"semantic_similarity": similarity}


@app.post("/interview-score")
async def interview_score(request: InterviewScoreRequest):
    match_result = match_resume_to_jd(request.resume, request.jd)
    ats_score = calculate_ats_score(request.resume, request.jd, match_result)
    semantic_score = calculate_similarity(request.resume_text, request.jd_text)
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
async def rewrite_resume(request: RewriteResumeRequest):
    match_result = match_resume_to_jd(request.resume, request.jd)
    before_score = calculate_ats_score(request.resume, request.jd, match_result)
    semantic_score = calculate_similarity(request.resume_text, request.jd_text)
    analysis = _build_analysis(
        ats_score=before_score, semantic_score=semantic_score,
        missing_skills=match_result["missing_skills"],
        matched_skills=match_result["matched_skills"],
        skill_match_score=match_result["skill_match_score"],
    )
    recommendations = RecommendationEngine.generate(analysis)
    optimizer = OptimizationLoop(
        max_passes=request.max_passes,
        num_candidates=request.num_candidates,
        rewrite_engine=REWRITE_ENGINE,
    )
    optimization = optimizer.optimize(
        resume=request.resume, jd=request.jd,
        resume_text=request.resume_text, jd_text=request.jd_text,
        recommendations=recommendations["recommendations"],
    )
    changes = DiffAnalyzer.analyze(
        before=request.resume_text, after=optimization["optimized_resume"],
    )["changes"]
    if optimization["accepted"]:
        try:
            append_rewrite_example(
                resume_before=request.resume_text,
                resume_after=optimization["optimized_resume"],
                jd=request.jd_text,
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
    }


@app.post("/evaluate-rewrite")
async def evaluate_rewrite(request: EvaluateRewriteRequest):
    """Stage 7: Multi-metric rewrite evaluation returning composite rewrite_quality score."""
    jd_keywords: list[str] = []
    for fname in ("required_skills", "preferred_skills", "technologies", "keywords"):
        val = request.jd.get(fname, [])
        if isinstance(val, list):
            jd_keywords.extend(str(v) for v in val if v)

    semantic_similarity = calculate_similarity(request.rewritten_text, request.jd_text)
    match_result = match_resume_to_jd(request.rewritten_resume, request.jd)
    ats_score = calculate_ats_score(request.rewritten_resume, request.jd, match_result)

    eval_result = REWRITE_EVALUATOR.evaluate(
        original_text=request.original_text,
        rewritten_text=request.rewritten_text,
        rewritten_resume=request.rewritten_resume,
        ats_score=ats_score,
        semantic_similarity=float(semantic_similarity),
        jd_keywords=jd_keywords,
    )
    return eval_result.to_dict()


@app.post("/interview-prep")
async def interview_prep(request: InterviewPrepRequest):
    """Stage 9: Generate interview questions and STAR answers from resume + JD."""
    result = INTERVIEW_ENGINE.generate(
        resume_text=request.resume_text,
        jd_text=request.jd_text,
        matched_skills=request.matched_skills,
        missing_skills=request.missing_skills,
    )
    return result.to_dict()


@app.post("/company-intel")
async def company_intel(request: CompanyIntelRequest):
    """Stage 10: Generate Company Intelligence Report (tech stack, interview process, salary, etc.)."""
    if not request.company.strip():
        raise HTTPException(status_code=400, detail="Company name cannot be empty.")
    report = COMPANY_INTEL_ENGINE.generate(
        company=request.company.strip(),
        role=request.role.strip() or "Software Engineer",
    )
    return report.to_dict()


@app.post("/export-resume")
async def export_resume_endpoint(request: ExportResumeRequest):
    """Convert optimized resume plain text into a formatted PDF or DOCX file."""
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text cannot be empty.")
    pkg = "python-docx" if request.format == "docx" else "reportlab"
    try:
        file_bytes, media_type, filename = export_resume(request.resume_text, request.format)
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependency for {request.format.upper()} export: {exc}. Run: pip install {pkg}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}") from exc

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/debug-rewrite")
async def debug_rewrite(request: RewriteResumeRequest):
    """Development endpoint: full optimisation trace."""
    match_result = match_resume_to_jd(request.resume, request.jd)
    original_ats_score = calculate_ats_score(request.resume, request.jd, match_result)
    semantic_score = calculate_similarity(request.resume_text, request.jd_text)
    analysis = _build_analysis(
        ats_score=original_ats_score, semantic_score=semantic_score,
        missing_skills=match_result["missing_skills"],
        matched_skills=match_result["matched_skills"],
        skill_match_score=match_result["skill_match_score"],
    )
    recommendations = RecommendationEngine.generate(analysis)
    optimizer = OptimizationLoop(
        max_passes=request.max_passes,
        num_candidates=request.num_candidates,
        rewrite_engine=REWRITE_ENGINE,
    )
    trace = optimizer.optimize_with_debug(
        resume=request.resume, jd=request.jd,
        resume_text=request.resume_text, jd_text=request.jd_text,
        recommendations=recommendations["recommendations"],
    )
    result = trace["result"]
    debug = trace["debug"]
    return {
        "original_resume": debug["original_resume"],
        "candidate_resume": debug["candidate_resume"],
        "parsed_original_resume": debug["parsed_original_resume"],
        "parsed_candidate_resume": debug["parsed_candidate_resume"],
        "original_ats_score": debug["original_ats_score"],
        "candidate_ats_score": debug["candidate_ats_score"],
        "accepted": debug["accepted"],
        "reason": debug["reason"],
        "result": result,
        "analysis": analysis,
        "recommendations": recommendations,
    }
