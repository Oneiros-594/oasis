from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="Oasis AI",
    description="Your personal AI assistant and interactive world platform.",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "app": "Oasis AI",
        "status": "online",
        "message": "Welcome to Oasis!",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:3b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Oasis, a helpful, thoughtful AI "
                            "companion. Be clear, friendly, and useful."
                        ),
                    },
                    {
                        "role": "user",
                        "content": request.message,
                    },
                ],
                "stream": False,
            },
        )

        response.raise_for_status()
        result = response.json()

    return {
        "reply": result["message"]["content"],
        "model": result["model"],
    }
