from pydantic import BaseModel, Field
from typing import List


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Raw academic notes to analyze.")

    model_config = {
        "json_schema_extra": {
            "example": {"text": "Photosynthesis is the process by which plants convert light into energy..."}
        }
    }


class ConceptResponse(BaseModel):
    topic: str
    key_concepts: List[str]
    examples: List[str]