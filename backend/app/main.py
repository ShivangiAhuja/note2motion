from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import TextInput, ConceptResponse
from app.agents.concept_agent import ConceptAgent

app = FastAPI(
    title="Note2Motion API",
    description="Converts academic notes into structured concept explanations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ConceptAgent()


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Note2Motion API is running."}


@app.post("/analyze-text", response_model=ConceptResponse, tags=["Analysis"])
async def analyze_text(payload: TextInput):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = await agent.analyze(payload.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))