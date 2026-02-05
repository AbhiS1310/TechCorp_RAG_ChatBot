import os
import subprocess
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import KNOWLEDGE_BASE_DIR
from src.pipeline.rag_pipeline import RagPipeline
from src.utils.logging import get_logger

# Initialize structured logger
logger = get_logger(__name__)

# Load environment variables (e.g., GROQ_API_KEY)
load_dotenv()

# Initialize the RAG pipeline (shared across requests)
pipeline = RagPipeline()

logger.info("TechCorp RAG Chatbot initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan hook.

    Runs once on application startup and shutdown.

    Startup responsibilities:
    - Build or load the vector index
    - Ensure the RAG pipeline is ready before serving traffic
    """
    logger.info("Starting TechCorp RAG Chatbot...")
    pipeline.rebuild()
    logger.info("Vector index ready")
    yield
    logger.info("Shutting down TechCorp RAG Chatbot")


# Create FastAPI application with lifespan management
app = FastAPI(
    title="TechCorp RAG Chatbot",
    lifespan=lifespan,
)

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to React frontend directory
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


# -----------------------------
# API Schemas
# -----------------------------

class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.
    """
    query: str


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    """
    answer: str
    sources: list[str]


# -----------------------------
# API Endpoints
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for answering HR policy questions.

    Flow:
    - Accept user query
    - Run through RAG pipeline
    - Return answer and citations
    """
    result = pipeline.answer_question(request.query)
    return ChatResponse(**result)


@app.post("/upload")
def upload(file: UploadFile = File(...)) -> dict:
    """
    Upload a new knowledge base document.

    Constraints:
    - Only .txt files are supported

    Behavior:
    - Saves file to knowledge_base directory
    - Rebuilds vector index to include new document
    """
    if not file.filename.endswith(".txt"):
        return {
            "status": "error",
            "message": "Only .txt files are supported.",
        }

    # Ensure knowledge base directory exists
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = KNOWLEDGE_BASE_DIR / file.filename
    content = file.file.read().decode("utf-8")
    file_path.write_text(content, encoding="utf-8")

    # Rebuild embeddings and FAISS index
    pipeline.rebuild()

    return {
        "status": "success",
        "message": f"Uploaded {file.filename} and rebuilt index.",
    }


# -----------------------------
# Frontend Launcher
# -----------------------------

def start_frontend() -> subprocess.Popen | None:
    """
    Start the React frontend development server (Vite).

    This is intended for local development only.
    """
    if not FRONTEND_DIR.exists():
        logger.warning("Frontend directory missing: %s", FRONTEND_DIR)
        return None

    logger.info("Starting frontend dev server...")

    # Windows compatibility for npm command
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    return subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "--host"],
        cwd=str(FRONTEND_DIR),
        shell=False,
        env={**os.environ},
    )


# -----------------------------
# Application Entry Point
# -----------------------------

if __name__ == "__main__":
    # Start frontend (non-blocking)
    start_frontend()

    # Start FastAPI backend
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",       
        access_log=True, 
    )
