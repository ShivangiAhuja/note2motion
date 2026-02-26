from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import TextInput, ConceptResponse, ScenePlanResponse
from app.agents.concept_agent import ConceptAgent
from app.agents.scene_agent import SceneAgent

app = FastAPI(
    title="Note2Motion API",
    description="Converts academic notes into structured concept explanations and video scene plans.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

concept_agent = ConceptAgent()
scene_agent = SceneAgent()


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Note2Motion API is running."}


@app.post("/analyze-text", response_model=ConceptResponse, tags=["Analysis"])
async def analyze_text(payload: TextInput):
    """Extract structured concepts from raw academic notes."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        return await concept_agent.analyze(payload.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-scenes", response_model=ScenePlanResponse, tags=["Scene Planning"])
async def generate_scenes(concept: ConceptResponse):
    """Convert a structured concept JSON into a scene-by-scene video breakdown."""
    if not concept.topic.strip():
        raise HTTPException(status_code=400, detail="Concept topic cannot be empty.")
    if not concept.key_concepts:
        raise HTTPException(status_code=400, detail="At least one key concept is required.")
    try:
        return await scene_agent.plan(concept)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))