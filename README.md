# DocQA 

DocQA is a specialized RAG system built with FastAPI, FAISS, Sentence-Transformers, and Groq. 
The application allows users to upload any book or story PDF, index its content, and then chat with a selected character from that book. The model responds in the style, voice, and characteristic tone of that character, grounded strictly in the factual context extracted from the document.

---

## System Flow

```mermaid
flowchart LR
subgraph group_api["FastAPI Service"]
  node_main["FastAPI App<br/>API orchestration<br/>[main.py]"]
  node_sample_pdf["Bundled Sample PDF<br/>default document"]
  node_upload_pdf["Uploaded PDF<br/>multipart input"]
end
subgraph group_ingestion["Indexing Pipeline"]
  node_pdf_utils["PDF Extractor &amp; Chunker<br/>ingestion<br/>[pdf_utils.py]"]
end
subgraph group_retrieval["Retrieval State"]
  node_encoder{{"Sentence-Transformers Encoder<br/>local embeddings<br/>[vector_store.py]"}}
  node_vector_store[("FAISS Vector Store<br/>in-memory similarity index<br/>[vector_store.py]")]
  node_chunk_text["Chunk Text Store<br/>in-memory context<br/>[vector_store.py]"]
end
subgraph group_generation["Grounded Generation"]
  node_persona["Persona Prompt Builder<br/>prompt orchestration<br/>[persona.py]"]
  node_groq{{"Groq Completion API<br/>remote LLM"}}
  node_groq_key["GROQ_API_KEY<br/>runtime secret<br/>[.env.example]"]
end
node_client(("API Client"))
node_requirements["Python Dependencies<br/>deployment manifest<br/>[requirements.txt]"]
node_client -->|"POST /upload or /chat"| node_main
node_sample_pdf -->|"startup default"| node_main
node_main -->|"stores multipart PDF"| node_upload_pdf
node_main -->|"indexes default or upload"| node_pdf_utils
node_pdf_utils -->|"text chunks"| node_encoder
node_encoder -->|"chunk embeddings"| node_vector_store
node_pdf_utils -->|"source chunks"| node_chunk_text
node_main -->|"chat question embedding"| node_encoder
node_encoder -->|"query vector"| node_vector_store
node_vector_store -->|"top-4 vector matches"| node_chunk_text
node_main -->|"character, question, passages"| node_persona
node_chunk_text -->|"retrieved context"| node_persona
node_persona -->|"grounded completion request"| node_groq
node_groq_key -.->|"authentication"| node_groq
node_groq -->|"answer or failure"| node_main
node_main -->|"JSON response"| node_client
node_requirements -.->|"runtime dependencies"| node_main
click node_main "https://github.com/aelaraby6/docqa/blob/main/src/main.py"
click node_sample_pdf "https://github.com/aelaraby6/docqa/blob/main/data/the_lighthouse_keepers_secret.pdf"
click node_pdf_utils "https://github.com/aelaraby6/docqa/blob/main/src/utils/pdf_utils.py"
click node_encoder "https://github.com/aelaraby6/docqa/blob/main/src/vector_store.py"
click node_vector_store "https://github.com/aelaraby6/docqa/blob/main/src/vector_store.py"
click node_chunk_text "https://github.com/aelaraby6/docqa/blob/main/src/vector_store.py"
click node_persona "https://github.com/aelaraby6/docqa/blob/main/src/persona.py"
click node_groq_key "https://github.com/aelaraby6/docqa/blob/main/.env.example"
click node_requirements "https://github.com/aelaraby6/docqa/blob/main/requirements.txt"
classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_main,node_sample_pdf,node_upload_pdf toneBlue
class node_pdf_utils toneAmber
class node_encoder,node_vector_store,node_chunk_text toneMint
class node_persona,node_groq,node_groq_key toneRose
class node_client,node_requirements toneNeutral
```

### Detailed Pipeline Breakdown

1. **Ingestion & Vector Indexing (`src/utils/pdf_utils.py`, `src/vector_store.py`)**:
   * **PDF Text Extraction**: Extracts text from the uploaded PDF document pages sequentially.
   * **Text Chunking**: Splits raw text into manageable chunks of 800 characters with a sliding overlap of 100 characters to maintain context boundaries.
   * **Embedding Generation**: Encodes text chunks into dense vectors using the pre-trained Hugging Face model `all-MiniLM-L6-v2`.
   * **Vector Storage**: Indexes and stores these embeddings in memory utilizing a FAISS `IndexFlatL2` index for lightning-fast Euclidean distance search.

2. **RAG & Chat Inference (`src/persona.py`, `src/main.py`)**:
   * **Query Encoding**: Converts the user's input question into a vector using the same SentenceTransformer model.
   * **Nearest Neighbor Search**: Queries the FAISS index to extract the `k=4` most semantically relevant text chunks.
   * **Prompt Construction**: Generates a custom system prompt directing the LLM to embody the target character, follow their speech style, and ground their knowledge strictly on the retrieved context chunks (refusing to invent facts if they lie outside the text).
   * **Inference**: Submits the constructed prompt and query to Llama-3.3-70b-versatile via Groq's high-speed API, returning the final stylized character response.

---

## Directory Layout

```text
DocQA/
├── data/
│   └── the_lighthouse_keepers_secret.pdf   # Sample story PDF used for startup auto-indexing
├── src/
│   ├── __init__.py
│   ├── main.py                             # FastAPI server & routes (/upload, /chat)
│   ├── persona.py                          # Prompt engineering & Groq Client setup
│   ├── vector_store.py                     # Embedding wrapper & FAISS index handlers
│   └── utils/
│       ├── __init__.py
│       └── pdf_utils.py                    # PDF readers & text splitter utilities
├── tests/
│   ├── __init__.py
│   └── test_sanity.py                      # Sanity check test script
├── uploads/                                # Target folder for uploaded books at runtime
├── .env                                    # Local environment secrets (Git ignored)
├── .env.example                            # Configuration environment template
├── .gitignore                              # Git exclusion file
├── requirements.txt                        # Dependency lists
└── README.md                               # Project documentation
```

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd DocQA
   ```

2. **Create and activate a virtual environment**:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add environment variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## How to Run & Verify

### 1. Verify index functionality (Sanity check)
Run the sanity test script to make sure the pipeline builds, embeds, and runs nearest-neighbor query retrieval:
```bash
python -m tests.test_sanity
```

### 2. Start the FastAPI API Server
Launch the FastAPI development environment:
```bash
uvicorn src.main:app --reload
```
Once the server is running, you can explore, test, and execute calls using the built-in swagger interface at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## API Documentation

* **`POST /upload`**: Replaces the currently indexed book with a new uploaded PDF.
  * **Request**: `file` (multipart/form-data)
  * **Response**: `{"status": "ok", "chunks_indexed": 12}`

* **`POST /chat`**: Ask questions and chat with the character.
  * **Request** (Form URL encoded):
    * `character_name` (string): The exact name of the character to interact with (e.g. `Silas Vane`).
    * `question` (string): The query statement or prompt.
  * **Response**: `{"character": "Silas Vane", "answer": "..."}`
