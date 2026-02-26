from pydantic import BaseModel, Field
from typing import List, Literal


# ── Concept Agent ─────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Raw academic notes to analyze.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Photosynthesis is the process by which plants convert light into energy..."
            }
        }
    }


class ConceptResponse(BaseModel):
    topic: str
    key_concepts: List[str]
    examples: List[str]


# ── Scene Planning Agent ───────────────────────────────────────────────────────

VisualType = Literal["diagram", "text_slide", "example", "code_demo"]


class Scene(BaseModel):
    scene_number: int
    scene_title: str
    narration: str
    visual_type: VisualType
    duration: int = Field(..., description="Estimated duration in seconds.")


class ScenePlanResponse(BaseModel):
    topic: str
    total_scenes: int
    estimated_total_duration: int = Field(..., description="Sum of all scene durations in seconds.")
    scenes: List[Scene]