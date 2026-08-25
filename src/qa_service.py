import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def build_system_prompt(context_chunks: list[str]) -> str:
    context = "\n---\n".join(context_chunks)
    return f"""You are a helpful assistant for question-answering tasks.
You must answer the user's question accurately and objectively based only on the retrieved context from the uploaded document provided below.

Strict Constraints:
1. Ground your answer strictly in the provided context.
2. If the answer is not present in the context or if there is insufficient information, state clearly that you cannot find the answer in the document. Do not attempt to make up or extrapolate facts not written in the context.
3. Keep the answer clear, concise, and professional.

Retrieved Context:
{context}
"""

def ask_document(question: str, context_chunks: list[str]) -> str:
    system_prompt = build_system_prompt(context_chunks)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.0,  
    )
    return response.choices[0].message.content
