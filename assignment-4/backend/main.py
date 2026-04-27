from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chat import router as chat_router
from .api.approval import router as approval_router
from .api.knowledge import router as knowledge_router
from .api.onboarding import router as onboarding_router

app = FastAPI(title="Personal Assistant API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(approval_router)
app.include_router(knowledge_router)
app.include_router(onboarding_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
