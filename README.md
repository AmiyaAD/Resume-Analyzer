# 📄 Resume Analyzer Chatbot

> An AI-powered resume analysis assistant that checks ATS compatibility, grammar, and recruiter-friendliness — built with LangChain, NVIDIA NIM (Nemotron LLMs), and multi-turn conversational memory.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C?style=flat-square)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-Nemotron_LLM-76B900?style=flat-square&logo=nvidia&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-Express_Frontend-339933?style=flat-square&logo=node.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎯 What It Does

Upload your resume and chat with an AI that tells you:

- ✅ **ATS Score** — Will your resume pass automated screening systems?
- ✍️ **Grammar & Tone** — Corrections for grammar, passive voice, and weak phrasing
- 🎯 **Recruiter Friendliness** — Is your resume easy to skim in 6 seconds?
- 💬 **Multi-turn Q&A** — Ask follow-up questions; the bot remembers the full conversation

---

## ✨ Features

- 📎 **Multi-format Upload** — Supports `.pdf`, `.docx`, and `.txt` files
- 🧠 **NVIDIA Nemotron LLM** — Powered via NVIDIA NIM API for high-quality analysis
- 🔗 **LangChain Orchestration** — Tool binding, function calling, and agent executor pipeline
- 💾 **Conversation Memory** — Full multi-turn context retained across the session
- ⚡ **FastAPI Backend** — Clean async REST endpoints for upload and chat
- 🖥️ **Node.js + Express Frontend** — Lightweight, fast, Vanilla JS UI

---

## 🏗️ Architecture

```
User Uploads Resume (.pdf / .docx / .txt)
            │
            ▼
    Node.js / Express Frontend
            │  REST API
            ▼
    FastAPI Backend
            ├── Text Extraction
            │       ├── pdfplumber   (.pdf)
            │       ├── python-docx  (.docx)
            │       └── plain read   (.txt)
            │
            ├── LangChain Agent
            │       ├── Conversation Memory Buffer
            │       ├── Tool: ATS Checker
            │       ├── Tool: Grammar Corrector
            │       └── Tool: Tone Analyzer
            │
            └── NVIDIA NIM API (Nemotron LLM)
                        │
                        ▼
                  Structured Analysis Response
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA NIM API key ([get one free](https://build.nvidia.com/))

### 1. Clone the repository
```bash
git clone https://github.com/AmiyaAD/resume-analyzer-chatbot.git
cd resume-analyzer-chatbot
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Fill in:
# NVIDIA_API_KEY=nvapi-...
```

### 4. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 5. Start the frontend
```bash
cd ../frontend
npm install
npm start
```

Open [http://localhost:3001](http://localhost:3001) and upload your resume.

---

## 💬 Example Interaction

```
You:  [uploads resume.pdf]

Bot:  I've analyzed your resume. Here's a quick summary:
      • ATS Score: 74/100 — Missing keywords for "Python Developer" roles
      • 3 grammar issues found (passive voice on lines 8, 14, 22)
      • Your summary section is strong, but bullet points lack metrics

You:  How do I fix the ATS score?

Bot:  To improve your ATS score, add these missing keywords to your
      skills section: "REST APIs", "CI/CD", "Docker". Also, your job
      titles should match common JD terminology exactly...

You:  Can you rewrite my summary section?

Bot:  Sure! Here's an improved version based on your experience...
```

---

## 📁 Project Structure

```
resume-analyzer-chatbot/
├── backend/
│   ├── main.py                     # FastAPI entry point
│   ├── agents/
│   │   └── resume_agent.py         # LangChain agent + memory
│   ├── extractors/
│   │   ├── pdf_extractor.py        # pdfplumber
│   │   ├── docx_extractor.py       # python-docx
│   │   └── txt_extractor.py
│   ├── tools/
│   │   ├── ats_checker.py
│   │   ├── grammar_tool.py
│   │   └── tone_analyzer.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   └── app.js                  # Vanilla JS chat UI
│   ├── server.js                   # Express server
│   └── package.json
├── .env.example
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | NVIDIA Nemotron via NIM API |
| Agent Orchestration | LangChain (tool binding + executor) |
| Conversation Memory | LangChain `ConversationBufferMemory` |
| Backend | FastAPI, Python |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Frontend Server | Node.js + Express |
| UI | Vanilla JavaScript, HTML, CSS |

---

## 🗺️ Roadmap

- [ ] Add job description input for targeted ATS matching
- [ ] Score resume against specific job titles
- [ ] Export improved resume as `.docx`
- [ ] Support for LinkedIn profile URL input
- [ ] Deploy on cloud (AWS / GCP)

---

## 📬 Contact

**Amiya Dhara**
- 🔗 [LinkedIn](https://linkedin.com/in/amiyadhara)
- 💻 [GitHub](https://github.com/AmiyaAD)
- 📧 amiyadhara10@gmail.com

---

<p align="center">Built with ❤️ by Amiya Dhara · MCA AI/ML · Sister Nivedita University</p>
