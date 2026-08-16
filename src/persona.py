import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_system_prompt(character_name: str, context_chunks: list[str]) -> str:
    context = "\n---\n".join(context_chunks)
    return f"""You are now embodying the character "{character_name}" from the attached book.
Speak in their style, tone, and characteristic phrases exactly as they appear in the context below.
Do not invent events or details that are not present in the context. If a question falls outside what
the character would know from the book, say so in the character's own voice.

Context from the book:
{context}
"""

def ask_character(character_name: str, question: str, context_chunks: list[str]) -> str:
    system_prompt = build_system_prompt(character_name, context_chunks)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.8,
    )
    return response.choices[0].message.content
