# ============================================================
# Garuda AI - FastAPI Backend
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestration.garuda_ai import analyze_with_garuda


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="Garuda AI API",
    description="Personal Cyber Safety Agent",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AnalyzeRequest(BaseModel):
    message: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Garuda AI",
        "message": "Garuda AI API is running"
    }


# ============================================================
# ANALYZE MESSAGE
# ============================================================

@app.post("/analyze")
async def analyze_message(request: AnalyzeRequest):

    result = await analyze_with_garuda(
        request.message
    )

    return result