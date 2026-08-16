import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from src.utils.pdf_utils import extract_text, chunk_text
from src.vector_store import book_index
from src.persona import ask_character

app = FastAPI(title="DocQA")

DEFAULT_PDF = "data/the_lighthouse_keepers_secret.pdf"
UPLOAD_DIR = "uploads"


def load_pdf_into_index(path: str) -> int:
    text = extract_text(path)
    chunks = chunk_text(text)
    book_index.build(chunks)
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


@app.post("/chat")
async def chat(character_name: str = Form(...), question: str = Form(...)):
    if not book_index.chunks:
        return {"error": "No book is indexed yet. Call /upload first."}

    relevant_chunks = book_index.search(question, k=4)
    answer = ask_character(character_name, question, relevant_chunks)
    return {"character": character_name, "answer": answer}
