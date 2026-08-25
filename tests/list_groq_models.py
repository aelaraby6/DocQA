import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key starts with: {api_key[:8] if api_key else 'None'}...")

try:
    client = Groq(api_key=api_key)
    models = client.models.list()
    print("\nAvailable models on your Groq account:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print("Error querying Groq models:", e)
