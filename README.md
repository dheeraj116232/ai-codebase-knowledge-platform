# 🧠 AI Codebase Knowledge Platform

> An AI-powered platform that reads, understands, and explains any GitHub codebase — turning unfamiliar repositories into navigable, queryable knowledge using Retrieval-Augmented Generation (RAG) and agentic AI.

![Status](https://img.shields.io/badge/status-active--development-brightgreen)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white)
![Frontend](https://img.shields.io/badge/frontend-Next.js-black?logo=next.js&logoColor=white)
![Language](https://img.shields.io/badge/language-Python%20%7C%20TypeScript-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 📖 Overview

**AI Codebase Knowledge Platform** lets a developer paste any public GitHub repository URL and instantly get an AI-generated understanding of it — file summaries, function-level explanations, dependency graphs, and natural-language answers to questions about how the code actually works.

It's built in incremental phases, moving from a working RAG-based MVP toward a full agentic developer-tools platform (VS Code integration, automated PR reviews, and more).

---

## ✨ Features

- 🔗 **Clone any GitHub repo** by pasting its URL — no manual setup required
- 🗂️ **Automatic code parsing** — walks the codebase and filters relevant source files
- 🧩 **AI-generated file summaries** — purpose, functions, classes, and dependencies at a glance
- 🔍 **Function-level explanations** — signature, parameters, return values, and step-by-step logic
- 🕸️ **Call graph analysis** — see what calls a function and what it calls in return
- 💬 **RAG-powered Q&A** — ask natural-language questions about the codebase and get context-aware answers
- 🤖 **Agentic AI workflows** *(in progress)* — multi-step reasoning over the codebase, not just single lookups
- ⚙️ **Developer tool integrations** *(planned)* — VS Code extension, automated PR review assistant

---

## 🏗️ Tech Stack

| Layer            | Technology                                  |
|-------------------|----------------------------------------------|
| Frontend          | Next.js, TypeScript, Tailwind CSS            |
| Backend           | FastAPI (Python)                             |
| Repo Handling     | GitPython                                    |
| AI / RAG          | Embeddings + vector search, LLM-based reasoning |
| Deployment        | Render (backend), Vercel-compatible frontend |

---

## 🗺️ Project Roadmap

The platform is built in four deliberate phases:

### Phase 1 — Working MVP (RAG)
- Project scaffolding (FastAPI + Next.js)
- Repository cloning via pasted GitHub URL
- Codebase parsing and file filtering
- Embedding generation and vector search
- Baseline retrieval-augmented Q&A

### Phase 2 — Code Intelligence
- AST-based code analysis
- File-level explanations (summary, functions, classes, dependencies)
- Function-level explanations (purpose, parameters, return values, flow)
- Call graph construction (who calls what)

### Phase 3 — Agentic AI
- Multi-step reasoning agents over the codebase
- Context-aware, cross-file question answering
- Autonomous exploration of unfamiliar code paths

### Phase 4 — Developer Tools
- VS Code extension for in-editor explanations
- Automated pull request review and summarization
- Additional IDE and CI/CD integrations

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone this repository
```bash
git clone https://github.com/<your-username>/ai-codebase-platform.git
cd ai-codebase-platform
```

### 2. Backend setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend runs at `http://localhost:8000` — check `/health` to confirm it's live.

### 3. Frontend setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

### 4. Try it out
Paste a public GitHub repository URL into the UI and click **Clone Repository** to begin analysis.

---

## 📡 API Overview

| Method | Endpoint      | Description                              |
|--------|---------------|-------------------------------------------|
| GET    | `/health`     | Service health check                      |
| POST   | `/clone`      | Clone a GitHub repository by URL          |
| POST   | `/explain/file`     | Get an AI-generated summary of a file |
| POST   | `/explain/function` | Get an AI-generated explanation of a function |
| GET    | `/callgraph`  | Retrieve function call graph for a file   |

*(Full API reference and request/response schemas available in `/docs` once the backend is running — powered by FastAPI's built-in Swagger UI.)*

---

## 📌 Notes & Known Limitations

- Input URLs are not currently sanitized for production-grade security — fine for a demo/portfolio project, but should be hardened before public deployment.
- Repository cloning is currently synchronous; large repositories may take a few seconds to process.
- Reranking of search results is a documented future enhancement, pending a lightweight (hosted API-based) implementation to avoid memory constraints on free-tier hosting.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

<p align="center">Built with FastAPI, Next.js, and a genuine curiosity about how codebases think.</p>