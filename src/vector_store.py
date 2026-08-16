import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

class BookIndex:
    def __init__(self):
        self.index = None
        self.chunks: list[str] = []

    def build(self, chunks: list[str]):
        self.chunks = chunks
        embeddings = model.encode(chunks, convert_to_numpy=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def search(self, query: str, k: int = 4) -> list[str]:
        query_vec = model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vec, k)
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

book_index = BookIndex()
