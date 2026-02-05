# TechCorp RAG Chatbot

A **production-grade Retrieval-Augmented Generation (RAG) system** designed to answer internal HR policy questions accurately in the presence of **conflicting document versions and irrelevant noise**.

The system ensures employees always receive **the most current, authoritative policy**, with **explicit source citations** for human verification.

---

## Key Capabilities

- ✅ **Conflict resolution** between outdated and current HR policies  
- ✅ **Noise tolerance** (irrelevant documents are ignored even if keywords overlap)  
- ✅ **Source-cited answers** for explainability and trust  
- ✅ **Deterministic LLM behavior** suitable for policy use cases  
- ✅ **Modular, production-ready architecture**

---

## Architecture Overview


```
[User]
|
v
[React + Tailwind UI]
|
v
[FastAPI Backend]
|   
|    --> /upload (new documents → re-embed)
v
[RAG Pipeline]
├── Retrieval (FAISS + SentenceTransformers)
├── Reranking (policy priority + recency)
├── Conflict Resolution (latest policy wins)
└── Answer Generation (Groq LLM + citations)
|
v
[Answer + Sources]

```

---

## Technology Stack

### Backend
- **Python 3.11**
- **FastAPI**
- **LangChain**
- **FAISS (local vector store)**
- **SentenceTransformers (embeddings)**
- **Groq LLM (deterministic inference)**

### Frontend
- **React**
- **Tailwind CSS**
- **Vite**

### Tooling
- **uv** (dependency & environment management)
- **dotenv** (configuration)

---

## Setup & Running

### Backend + Frontend (Single Command)

```bash
git clone https://github.com/AbhiS1310/TechCorp_RAG_ChatBot.git
cd TechCorp_RAG_ChatBot
uv sync
cp .env.example .env
cd frontend
npm install
npm run build
cd ..
uv run python main.py
````

`main.py` starts **both**:

* the FastAPI backend (`http://localhost:8000`)
* the React frontend (Vite dev server)

---

## Environment Variables

Edit `.env` and set:

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant  # optional
```

---

## Frontend (Optional Manual Start)

```bash
cd frontend
npm run dev
```

---

## Example Queries & Expected Behavior

### Conflict Resolution

**Query:**

> Can I work fully remotely?

**Expected Behavior:**

* Identifies that the 2021 policy is revoked
* Uses **only** `policy_v2_2024.txt`

**Example Answer:**

```
No, fully remote work is no longer allowed. Employees are expected to be in the office four days per week, with remote work limited to one day per week subject to manager approval.

Sources: policy_v2_2024.txt
```

---

### Noise Filtering

**Query:**

> Can I work remotely this Friday?

**Expected Behavior:**

* Ignores cafeteria menu despite keyword overlap (“Friday”)
* Uses only the HR policy
* Returns a single authoritative citation

---

## Design Decisions

* **Metadata-driven authority**
  Documents are classified as `policy` or `noise`. Only policy documents are indexed and used for generation.

* **Explicit conflict resolution**
  When multiple policies exist, the most recent `effective_date` always wins.

* **Noise-safe retrieval**
  Irrelevant documents may exist in storage but are filtered before generation.

* **Deterministic generation**
  LLM temperature is set to `0` to ensure repeatable, auditable outputs.

* **Explainability by design**
  Every response includes explicit source filenames.

---

## Project Structure

```
techcorp-rag-chatbot/
│
├── knowledge_base/        # HR policies + noise documents
│
├── src/
│   ├── ingestion/         # loading, metadata, embeddings
│   ├── retrieval/         # retrieval, reranking, resolution
│   ├── generation/        # prompts + LLM calls
│   ├── pipeline/          # end-to-end RAG orchestration
│   └── utils/             # logging and helpers
│
├── frontend/              # React + Tailwind UI
├── main.py                # Backend + frontend launcher
├── requirements.txt
└── README.md
```

---

## Limitations

* Reranking uses heuristic scoring (no cross-encoder yet)
* Effective date parsing supports common formats only
* No authentication (intended for internal demo use)

---

## Future Improvements

* Cross-encoder reranking for higher precision
* Document versioning and lifecycle management
* Automated evaluation tests and CI
* Authentication and role-based access
* Streaming responses and confidence scoring

---

## Summary

This project demonstrates **production-ready RAG engineering**, with:

* Accurate conflict resolution
* Robust noise resistance
* Explainable, source-grounded answers
* Clean, extensible architecture

Designed to reflect **real-world internal enterprise use cases**, not just a demo.
