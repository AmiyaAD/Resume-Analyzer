from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import pdfplumber
import docx
from io import BytesIO
from typing import List, TypedDict
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your Node frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


llm = ChatOpenAI(
  model="nvidia/nemotron-3-super-120b-a12b",
  api_key="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", 
  base_url="https://integrate.api.nvidia.com/v1"
)



async def ats_checker(state: ResumeState):
    """Check ATS keyword matches in resume text."""
    text = state["resume_text"].lower()
    keywords = state["job_keywords"]
    matched = [kw for kw in keywords if kw.lower() in text]
    missing = [kw for kw in keywords if kw.lower() not in text]
    state["ats_score"] = f"{len(matched)}/{len(keywords)}"
    state["matched_keywords"] = matched
    state["missing_keywords"] = missing
    return state

async def grammar_tool(state: ResumeState):
    """Correct grammar in resume text using LLM."""
    try:
        response = await llm.ainvoke([HumanMessage(content=f"Correct grammar: {state['resume_text']}")])
        state["corrections"] = response.content
    except Exception as e:
        state["corrections"] = f"Error correcting grammar: {str(e)}"
    return state

async def tone_tool(state: ResumeState):
    """Rewrite resume text in recruiter-friendly tone using LLM."""
    try:
        response = await llm.ainvoke([HumanMessage(content=f"Rewrite recruiter-friendly: {state['resume_text']}")])
        state["suggestions"] = response.content
    except Exception as e:
        state["suggestions"] = f"Error rewriting tone: {str(e)}"
    return state


graph = StateGraph(ResumeState)
graph.add_node("ATS", ats_checker)
graph.add_node("Grammar", grammar_tool)
graph.add_node("Tone", tone_tool)

graph.add_edge(START, "ATS")
graph.add_edge("ATS", "Grammar")
graph.add_edge("Grammar", "Tone")
graph.add_edge("Tone", END)

graph_app = graph.compile()



async def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file.filename.endswith(".docx"):
        doc = docx.Document(BytesIO(await file.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return (await file.read()).decode("utf-8", errors="ignore")

def clean_keywords(raw_keywords: str) -> List[str]:
    return [kw.strip() for kw in raw_keywords.split(",") if kw.strip()]



@app.post("/analyze_resume/", response_model=ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile, job_keywords: str = Form("")):
    text = await extract_text(file)
    keywords = clean_keywords(job_keywords)

    state: ResumeState = {
        "resume_text": text,
        "job_keywords": keywords,
        "ats_score": "",
        "corrections": "",
        "suggestions": "",
        "matched_keywords": [],
        "missing_keywords": []
    }

    result = await graph_app.ainvoke(state)

    return ResumeAnalysisResponse(
        ats_score=result["ats_score"],
        corrections=result["corrections"],
        suggestions=result["suggestions"],
        matched_keywords=result["matched_keywords"],
        missing_keywords=result["missing_keywords"]
    )




