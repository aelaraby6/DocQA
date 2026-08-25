import asyncio
import os
from src.main import get_status, chat

async def verify_backend():
    print("=== Testing FastAPI Endpoint Handlers ===")
    
    # 1. Test /status endpoint
    print("\n1. Calling GET /status...")
    status = await get_status()
    print("Result:", status)
    assert status["status"] == "ready", "Index should be auto-loaded and ready!"
    assert "the_lighthouse_keepers_secret.pdf" in status["filename"], "Filename should match default!"
    
    # 2. Test /chat endpoint
    print("\n2. Calling POST /chat...")
    chat_response = await chat(
        question="What does Silas Vane believe about the sea?"
    )
    print("Result:", chat_response)
    assert "answer" in chat_response
    print("\nAnswer received:\n", chat_response["answer"])
    print("\n=== Backend Verification Completed Successfully! ===")

if __name__ == "__main__":
    # Ensure .env is loaded
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run verification
    asyncio.run(verify_backend())
