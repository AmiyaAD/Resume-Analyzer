import os
import asyncio
import logging
from io import BytesIO
from typing import List, TypedDict

import pdfplumber
import docx
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END, START
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY environment variable is not set")

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b",
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=120,
    max_retries=2,
)


class ResumeState(TypedDict):
    resume_text: str
    job_keywords: List[str]
    ats_score: str
    corrections: str
    suggestions: str
    matched_keywords: List[str]
    missing_keywords: List[str]



class ResumeAnalysisResponse(BaseModel):
    ats_score: str
    corrections: str
    suggestions: str
    matched_keywords: List[str]
    missing_keywords: List[str]



async def ats_checker(state: ResumeState) -> ResumeState:
    """Keyword match against job description keywords."""
    text = state["resume_text"].lower()
    matched = [kw for kw in state["job_keywords"] if kw.lower() in text]
    missing = [kw for kw in state["job_keywords"] if kw.lower() not in text]
    total = len(state["job_keywords"])
    return {
        **state,
        "ats_score": f"{len(matched)}/{total}" if total else "N/A (no keywords provided)",
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


async def grammar_tool(state: ResumeState) -> ResumeState:
    """Fix grammar and improve clarity while preserving meaning."""
    prompt = (
        "You are a professional resume editor. "
        "Correct all grammar, spelling, and punctuation errors in the resume below. "
        "Preserve the original structure and meaning exactly. "
        "Return only the corrected resume text with no explanation.\n\n"
        f"RESUME:\n{state['resume_text']}"
    )
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        corrections = response.content.strip()
    except Exception as e:
        logger.error("Grammar tool error: %s", e)
        corrections = f"Grammar correction unavailable: {e}"
    return {**state, "corrections": corrections}


async def tone_tool(state: ResumeState) -> ResumeState:
    """Rewrite in a strong, action-oriented, recruiter-friendly tone."""
    prompt = (
        "You are an expert resume coach. "
        "Rewrite the resume below using strong action verbs, quantified achievements where possible, "
        "and a confident, professional tone suitable for a competitive job application. "
        "Keep all factual information intact. "
        "Return only the rewritten resume text with no explanation.\n\n"
        f"RESUME:\n{state['resume_text']}"
    )
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        suggestions = response.content.strip()
    except Exception as e:
        logger.error("Tone tool error: %s", e)
        suggestions = f"Tone rewrite unavailable: {e}"
    return {**state, "suggestions": suggestions}


async def parallel_llm_node(state: ResumeState) -> ResumeState:
    """Run grammar and tone rewrites concurrently to halve latency."""
    grammar_state, tone_state = await asyncio.gather(
        grammar_tool(state),
        tone_tool(state),
    )
    return {**state, "corrections": grammar_state["corrections"], "suggestions": tone_state["suggestions"]}


graph = StateGraph(ResumeState)
graph.add_node("ATS", ats_checker)
graph.add_node("LLMRewrite", parallel_llm_node)

graph.add_edge(START, "ATS")
graph.add_edge("ATS", "LLMRewrite")
graph.add_edge("LLMRewrite", END)

graph_app = graph.compile()


def _validate_file(file: UploadFile) -> None:
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


async def extract_text(file: UploadFile) -> str:
    """Read and extract plain text from PDF, DOCX, or plain-text files."""
    raw = await file.read()

    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit.",
        )

    filename = file.filename.lower()
    try:
        if filename.endswith(".pdf"):
            with pdfplumber.open(BytesIO(raw)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages).strip()

        if filename.endswith(".docx"):
            doc = docx.Document(BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs).strip()

        return raw.decode("utf-8", errors="ignore").strip()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Text extraction failed: %s", e)
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")


def clean_keywords(raw: str) -> List[str]:
    return [kw.strip() for kw in raw.split(",") if kw.strip()]



@app.post("/analyze_resume/", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile,
    job_keywords: str = Form(""),
) -> ResumeAnalysisResponse:
    _validate_file(file)

    text = await extract_text(file)
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract any text from the uploaded file.")

    keywords = clean_keywords(job_keywords)

    initial_state: ResumeState = {
        "resume_text": text,
        "job_keywords": keywords,
        "ats_score": "",
        "corrections": "",
        "suggestions": "",
        "matched_keywords": [],
        "missing_keywords": [],
    }

    try:
        result = await graph_app.ainvoke(initial_state)
    except Exception as e:
        logger.error("Graph execution error: %s", e)
        raise HTTPException(status_code=500, detail="Analysis pipeline failed. Please try again.")

    return ResumeAnalysisResponse(
        ats_score=result["ats_score"],
        corrections=result["corrections"],
        suggestions=result["suggestions"],
        matched_keywords=result["matched_keywords"],
        missing_keywords=result["missing_keywords"],
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}