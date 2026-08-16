from src.utils.pdf_utils import extract_text, chunk_text
from src.vector_store import book_index

text = extract_text("data/the_lighthouse_keepers_secret.pdf")
chunks = chunk_text(text)
book_index.build(chunks)

results = book_index.search("what does Silas always say?")
print("Sanity Check Search Results:")
for r in results:
    print(f"- {r}")
