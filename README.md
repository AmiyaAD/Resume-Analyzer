# Resume Analyzer Chatbot

An interactive chatbot that analyzes resumes for **ATS compatibility**, **grammar corrections**, and **recruiter-friendly tone**.  
Built with **FastAPI (backend)** and **Node.js/Express (frontend)**.

---

## 🚀 Features
- Upload resumes (`.pdf`, `.docx`, `.txt`)
- Extract text and check ATS keyword matches
- Grammar correction using NVIDIA LLMs
- Rewrite in recruiter-friendly tone
- Multi-turn memory (resume remembered across chat)


---

## 🛠️ Tech Stack
- **Backend:** FastAPI, LangChain, NVIDIA Nemotron models
- **Frontend:** Node.js, Express, Vanilla JS
- **LLM API:** NVIDIA NIM (via `NVIDIA_API_KEY`)
- **File Parsing:** `pdfplumber`, `python-docx`

---

## 📂 Project Structure

Resume-Analyzer/
│── main.py              # FastAPI backend
│── requirements.txt     # Python dependencies
│── server.js            # Express frontend server
│── package.json         # Node.js dependencies
│── public/              # Frontend static files
│    ├── index.html
│    ├── app.js
│    └── style.css
│── .env                 # Environment variables (ignored by git)
│── .gitignore           # Ignore node_modules, venv, .env, etc.


---

## ⚙️ Setup Instructions

### 1. Backend (FastAPI)
```bash
# Create virtual environment
python -m venv venv( I Also use Uv --> uv init .)
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt or (uv add -r requirements.txt)

# Run backend
uvicorn main:app --reload --port 8001

2. Frontend (Node.js)

# Install dependencies
npm install

# Run frontend
npm start

🔑 Environment Variables
Create a .env file in the project root:

NVIDIA_API_KEY=your_nvidia_api_key_here

🧪 Usage
Start backend (uvicorn main:app --reload --port 8001)

Start frontend (npm start)

Open http://localhost:3000

Upload a resume and type job keywords

Chatbot will return ATS score, corrections, and recruiter-friendly suggestions


<img width="545" height="263" alt="image" src="https://github.com/user-attachments/assets/072cfe14-a495-45a7-b899-44f14337d5d2" />
