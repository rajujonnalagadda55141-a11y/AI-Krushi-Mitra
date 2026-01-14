from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import requests
import logging
import time
import os

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(title="AI Krushi Mitra", description="Agriculture RAG Assistant", version="1.0")

origins = ["http://localhost:3000", "https://example.com"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SYSTEM_PROMPT = """..."""  # same as your SYSTEM_PROMPT
WEATHER_RULES = """..."""   # same
DISCLAIMER_TEXT = """...""" # same

# Config via env
FAISS_PATH = os.getenv("FAISS_PATH", "backend/embeddings/faiss_index")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")

def ask_ollama(system_prompt: str, context: str, question: str) -> str:
    prompt = f"""{system_prompt}\n\nContext:\n{context}\n\nWeather Rules:\n{WEATHER_RULES}\n\nQuestion:\n{question}"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 256}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Be tolerant of different response shapes
        if isinstance(data, dict):
            for key in ("response", "text", "answer"):
                if key in data and data[key]:
                    return str(data[key]).strip()
            # sometimes nested choices/text
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                c = data["choices"][0]
                if isinstance(c, dict):
                    return (c.get("text") or c.get("message") or c.get("content") or "").strip()
        # fallback to raw text
        return resp.text.strip() or "AI returned empty response."
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama API failure: {e}")
        return "AI service is temporarily unavailable. Please try again later."

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str

@app.on_event("startup")
def startup_event():
    logging.info("Starting up: initializing embeddings and vector DB...")
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if not os.path.exists(FAISS_PATH):
            logging.warning(f"FAISS path does not exist: {FAISS_PATH}")
            app.state.db = None
            logging.info("Continuing without vector DB; search will return helpful message.")
            return
        db = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        app.state.embeddings = embeddings
        app.state.db = db
        logging.info("FAISS index and embeddings loaded successfully")
    except Exception as e:
        logging.exception(f"Failed to load FAISS or embeddings at startup: {e}")
        app.state.db = None

@app.get("/")
def root():
    return {"message": "AI Krushi Mitra backend is running"}

@app.get("/health")
def health():
    db_status = "loaded" if getattr(app.state, "db", None) else "not_loaded"
    return {"status": "ok", "db_status": db_status, "message": "Backend healthy"}

@app.post("/ask", response_model=AskResponse)
def ask_ai(request: AskRequest) -> AskResponse:
    start_time = time.time()
    query = request.question.strip()
    logging.info(f"QUESTION | {query}")

    if not query:
        logging.warning("EMPTY_QUERY")
        raise HTTPException(status_code=400, detail="Please ask your farming question clearly.")
    if len(query) > 1000:
        logging.warning("LONG_QUERY")
        raise HTTPException(status_code=400, detail="Please ask a shorter question.")
    NON_AGRI_KEYWORDS = ["movie", "cricket", "actor", "song", "politics"]
    if any(word in query.lower() for word in NON_AGRI_KEYWORDS):
        logging.warning("NON_AGRI_QUERY")
        raise HTTPException(status_code=400, detail="I can help only with agriculture and farming questions.")

    db = getattr(app.state, "db", None)
    if db is None:
        logging.info("NO_VECTOR_DB")
        answer = "Vector DB not available. Please try later or contact admin.\n\nConfidence: Low"
        return AskResponse(question=query, answer=answer)

    docs = db.similarity_search(query, k=1)
    if not docs:
        logging.info("NO_CONTEXT_FOUND")
        answer = "I am not sure. Please consult a local agriculture officer.\n\nConfidence: Low"
        return AskResponse(question=query, answer=answer)

    context = "\n".join([d.page_content for d in docs])
    answer = ask_ollama(system_prompt=SYSTEM_PROMPT, context=context, question=query)

    response_time = round(time.time() - start_time, 2)
    logging.info(f"RESPONSE_TIME | {response_time} seconds")
    if response_time > 10:
        logging.warning(f"SLOW_RESPONSE | {response_time} seconds")

    final_answer = f"{answer}\n\n{DISCLAIMER_TEXT}"
    return AskResponse(question=query, answer=final_answer)
