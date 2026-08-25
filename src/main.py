import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from src.utils.pdf_utils import extract_text, chunk_text
from src.vector_store import book_index
from src.qa_service import ask_document

app = FastAPI(title="DocQA")

DEFAULT_PDF = "data/the_lighthouse_keepers_secret.pdf"
UPLOAD_DIR = "uploads"


def load_pdf_into_index(path: str) -> int:
    text = extract_text(path)
    chunks = chunk_text(text)
    filename = os.path.basename(path)
    book_index.build(chunks, filename=filename)
    return len(chunks)


@app.on_event("startup")
async def startup_event():
    """Auto-load the default PDF already sitting in the data folder,
    so you don't have to call /upload every time you restart the server."""
    if os.path.exists(DEFAULT_PDF):
        count = load_pdf_into_index(DEFAULT_PDF)
        print(f"[startup] Loaded default PDF '{DEFAULT_PDF}' -> {count} chunks indexed.")
    else:
        print(f"[startup] No default PDF found at '{DEFAULT_PDF}'. Use /upload to index one.")


@app.post("/upload")
async def upload_book(file: UploadFile = File(...)):
    """Upload a different PDF at any time to replace the currently indexed book."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    count = load_pdf_into_index(path)
    return {"status": "ok", "chunks_indexed": count}


@app.get("/status")
async def get_status():
    if not book_index.chunks:
        return {
            "status": "empty",
            "filename": None,
            "chunks_indexed": 0
        }
    return {
        "status": "ready",
        "filename": book_index.filename,
        "chunks_indexed": len(book_index.chunks)
    }


@app.post("/chat")
async def chat(question: str = Form(...)):
    if not book_index.chunks:
        return {"error": "No book is indexed yet. Call /upload first."}

    relevant_chunks = book_index.search(question, k=4)
    answer = ask_document(question, relevant_chunks)
    return {"answer": answer}
