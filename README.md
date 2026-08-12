# 🧠 AI Codebase Knowledge Platform

> **Understand any codebase faster.**
> An AI-powered developer platform that analyzes GitHub repositories, extracts code intelligence, builds dependency relationships, and provides context-aware explanations and answers using **RAG, AST analysis, and LLM-based reasoning**.

<p align="center">

![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge\&logo=next.js\&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge\&logo=typescript\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-api">API</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 📌 Overview

Understanding an unfamiliar software repository can require hours of manually reading files, tracing imports, following function calls, and searching for documentation.

The **AI Codebase Knowledge Platform** is designed to reduce that effort.

A developer provides a public GitHub repository URL, and the platform:

```text
GitHub Repository
       │
       ▼
Repository Cloning
       │
       ▼
Codebase Discovery
       │
       ▼
Source File Filtering
       │
       ▼
AST / Structural Analysis
       │
       ├──────────────► File Intelligence
       │
       ├──────────────► Function Intelligence
       │
       └──────────────► Dependency / Call Graph
       │
       ▼
Knowledge Retrieval
       │
       ▼
LLM Reasoning
       │
       ▼
Context-Aware Developer Answers
```

The goal is to evolve the platform from a codebase-aware RAG system into an **agentic developer assistant capable of autonomously exploring and reasoning about software repositories**.

---

# ✨ Core Capabilities

### 🔗 Repository Intelligence

* Clone public GitHub repositories from a URL
* Automatically discover repository structure
* Traverse source directories
* Filter relevant source files
* Extract useful code artifacts

### 🧩 Code Understanding

* File-level code analysis
* Function-level explanations
* Class and dependency identification
* AST-based structural analysis
* Code relationship extraction

### 🕸️ Dependency & Call Graph

Analyze relationships between functions and modules to help developers understand:

```text
Module A
   │
   ├── imports → Module B
   │
   └── calls → Function X
                    │
                    └── calls → Function Y
```

This makes it easier to trace execution paths through unfamiliar code.

### 💬 RAG-Powered Codebase Q&A

Ask natural-language questions such as:

> "Where is authentication handled?"

> "How does the repository process uploaded files?"

> "Which function generates the dependency graph?"

> "What happens after a repository is cloned?"

The system retrieves relevant code context before generating an answer.

### 🤖 Agentic AI — In Development

The next stage introduces agentic workflows capable of:

* Exploring multiple files
* Following dependencies
* Reasoning across modules
* Gathering relevant context
* Performing multi-step codebase investigation

### 🛠️ Developer Tooling — Planned

Future integrations include:

* VS Code extension
* AI-powered pull request review
* PR summarization
* CI/CD integration
* IDE-aware code explanations

---

# 🏗️ Architecture

## High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      Developer       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Next.js Frontend   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌──────────────┐       ┌──────────────┐
      │ GitHub Repo │       │ AST Analysis │       │  Retrieval   │
      │   Cloning   │       │   Engine     │       │    Layer     │
      └──────┬──────┘       └──────┬───────┘       └──────┬───────┘
             │                     │                      │
             └─────────────────────┼──────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │   Code Knowledge     │
                         │      Layer           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    LLM / RAG Layer   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Context-Aware Answer │
                         └──────────────────────┘
```

---

# 🔄 Codebase Analysis Pipeline

```text
1. GitHub URL
      ↓
2. Repository Clone
      ↓
3. Repository Traversal
      ↓
4. Source File Detection
      ↓
5. Code Parsing
      ↓
6. AST Extraction
      ↓
7. Function / Class Extraction
      ↓
8. Dependency Analysis
      ↓
9. Call Graph Construction
      ↓
10. Knowledge / Retrieval Layer
      ↓
11. LLM Context Construction
      ↓
12. AI Explanation / Q&A
```

This architecture separates **deterministic code analysis** from **probabilistic LLM reasoning**, improving the reliability of the overall system.

---

# 🧠 AI & Code Intelligence

The platform combines several complementary approaches.

| Component           | Purpose                                     |
| ------------------- | ------------------------------------------- |
| AST Analysis        | Understand code structure deterministically |
| File Analysis       | Identify purpose and important components   |
| Function Analysis   | Explain signatures, parameters and logic    |
| Dependency Analysis | Identify relationships between modules      |
| Call Graph          | Trace function-to-function relationships    |
| Embeddings          | Represent code semantically                 |
| Vector Retrieval    | Retrieve relevant code context              |
| RAG                 | Ground LLM responses in repository context  |
| LLM                 | Generate explanations and answers           |
| Agentic Workflows   | Perform multi-step repository investigation |

---

# 🧱 Tech Stack

## Frontend

* **Next.js**
* **React**
* **TypeScript**
* **Tailwind CSS**

## Backend

* **Python**
* **FastAPI**
* **Uvicorn**
* **GitPython**

## Code Intelligence

* Python AST
* Dependency analysis
* Call graph construction
* Static code inspection

## AI / GenAI

* Large Language Models
* Embeddings
* Vector retrieval
* Retrieval-Augmented Generation
* Agentic workflows

## Deployment

* **Render** — Backend
* **Vercel-compatible deployment** — Frontend

---

# 📁 Project Structure

```text
ai-codebase-platform/
│
├── backend/
│   ├── models/
│   ├── services/
│   │   ├── ast_service.py
│   │   ├── explain_service.py
│   │   └── prompt_builder.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── README.md
└── LICENSE
```

> Project structure may evolve as additional agentic and developer-tooling components are introduced.

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python **3.10+**
* Node.js **18+**
* npm
* Git

---

## 1. Clone the repository

```bash
git clone https://github.com/dheeraj116232/ai-codebase-knowledge-platform.git

cd ai-codebase-knowledge-platform
```

---

## 2. Backend Setup

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 💻 Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🧪 Example Workflow

### Step 1

Open the web application.

### Step 2

Paste a public GitHub repository URL.

### Step 3

Select:

**Clone Repository**

### Step 4

The backend analyzes the repository.

### Step 5

The platform extracts:

* Repository structure
* Files
* Functions
* Classes
* Dependencies
* Call relationships

### Step 6

Use the AI interface to ask questions about the repository.

Example:

```text
How does authentication work in this project?
```

The system retrieves relevant code context and generates an explanation.

---

# 📡 API

| Method | Endpoint            | Purpose                         |
| ------ | ------------------- | ------------------------------- |
| `GET`  | `/health`           | Backend health check            |
| `POST` | `/clone`            | Clone a GitHub repository       |
| `POST` | `/explain/file`     | Generate a file explanation     |
| `POST` | `/explain/function` | Explain a function              |
| `GET`  | `/callgraph`        | Retrieve call graph information |

Once the backend is running, the complete interactive API documentation is available through:

```text
/docs
```

FastAPI automatically provides Swagger/OpenAPI documentation.

---

# 🗺️ Development Roadmap

## ✅ Phase 1 — Repository Intelligence

* [x] FastAPI backend
* [x] Next.js frontend
* [x] GitHub repository cloning
* [x] Repository traversal
* [x] Source-file filtering
* [x] Initial code analysis
* [x] RAG foundation

## ✅ Phase 2 — Code Intelligence

* [x] AST-based analysis
* [x] File explanations
* [x] Function explanations
* [x] Dependency analysis
* [x] Call graph generation

## 🚧 Phase 3 — Agentic Code Intelligence

* [ ] Multi-step codebase reasoning
* [ ] Autonomous repository exploration
* [ ] Cross-file reasoning
* [ ] Context-aware investigation agents
* [ ] Improved retrieval and reranking
* [ ] Repository-level task planning

## 🔮 Phase 4 — Developer Platform

* [ ] VS Code extension
* [ ] AI pull-request review
* [ ] Automated PR summaries
* [ ] CI/CD integration
* [ ] IDE-aware code explanations
* [ ] Autonomous debugging workflows

---

# 🔐 Security & Production Considerations

The current implementation is primarily designed for **development, experimentation, and portfolio demonstration**.

Before production deployment, several areas should be hardened:

* Repository URL validation
* SSRF protection
* Repository size limits
* Clone timeouts
* Resource quotas
* Sandboxed code analysis
* Authentication and authorization
* Rate limiting
* Secret/API-key protection
* Malicious repository handling
* Dependency security scanning

These considerations are particularly important because the platform processes **externally supplied repositories**.

---

# ⚡ Current Limitations

* Repository cloning is currently synchronous.
* Large repositories may require additional processing time.
* Public GitHub repositories are the primary supported input.
* Retrieval quality can vary depending on repository structure.
* Production-grade URL and repository security hardening is still required.
* Advanced reranking and autonomous agent workflows are under development.

---

# 🎯 Why This Project?

Modern software repositories can contain thousands of files and millions of lines of code.

Traditional search answers:

> **"Where is this code?"**

This project aims to answer:

> **"How does this code work, why does it work this way, and what happens if I change it?"**

The long-term objective is to build a **developer intelligence layer** that sits between the developer and the complexity of large software systems.

---

# 📈 Future Vision

```text
                 ┌──────────────────────────┐
                 │       Developer          │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ AI Codebase Understanding│
                 └────────────┬─────────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        Understand        Explain          Navigate
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  AI Code Agent  │
                     └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
            Plan           Modify           Test
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                     Software Development
```

The eventual goal is not simply a **"chat with your codebase"** application.

It is to build an AI system that can **understand software, reason across its architecture, navigate dependencies, plan changes, and eventually assist with implementation and validation.**

---

# 🤝 Contributing

Contributions, suggestions, issues, and feature requests are welcome.

### Contribution workflow

```bash
git checkout -b feature/your-feature

git add .

git commit -m "Add: your feature"

git push origin feature/your-feature
```

Then open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for details.

---

# 👨‍💻 Author

## Dheeraj Kumar

**AI Engineer | Generative AI | Agentic AI | Machine Learning | Data Science**

🎓 NIT Tiruchirappalli

### Connect

* GitHub: [@dheeraj116232](https://github.com/dheeraj116232)
* Project: [AI Codebase Knowledge Platform](https://github.com/dheeraj116232/ai-codebase-knowledge-platform)

---

<p align="center">

### 🧠 Understand Code.

### 🔍 Discover Dependencies.

### 🤖 Build with AI.

**Built with FastAPI, Next.js, Python, TypeScript, and a genuine curiosity about how software works.**

⭐ If you find this project interesting, consider starring the repository.

</p>
