import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class DocQAAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip('/')

    def get_status(self) -> dict | None:
        try:
            res = requests.get(f"{self.base_url}/status", timeout=5)
            if res.status_code == 200:
                return res.json()
        except requests.exceptions.RequestException:
            pass
        return None

    def upload_file(self, file_name: str, file_bytes: bytes) -> tuple[bool, str]:
        """Upload a PDF book to the backend"""
        try:
            files = {"file": (file_name, file_bytes, "application/pdf")}
            res = requests.post(f"{self.base_url}/upload", files=files, timeout=60)
            if res.status_code == 200:
                return True, "Successfully indexed!"
            return False, f"Upload failed: {res.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def ask_document(self, question: str) -> tuple[bool, str]:
        """Send a question and retrieve response grounded in document context"""
        try:
            data = {
                "question": question
            }
            res = requests.post(f"{self.base_url}/chat", data=data, timeout=30)
            if res.status_code == 200:
                answer = res.json().get("answer", "No answer received.")
                return True, answer
            return False, f"Error {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
