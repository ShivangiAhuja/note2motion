import json
import logging
from app.models.schemas import ConceptResponse
from app.utils.config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert educator. Given academic notes, extract structured information.

Respond ONLY with a valid JSON object in this exact format:
{
  "topic": "<main topic as a short phrase>",
  "key_concepts": ["<concept 1>", "<concept 2>", "..."],
  "examples": ["<example 1>", "<example 2>", "..."]
}

Rules:
- topic: single concise phrase
- key_concepts: 3–7 core ideas from the text
- examples: 2–4 concrete examples or analogies mentioned or implied
- No markdown, no extra text — pure JSON only."""


class ConceptAgent:
    async def analyze(self, text: str) -> ConceptResponse:
        if config.USE_PLACEHOLDER:
            logger.warning("OPENAI_API_KEY not set — returning placeholder response.")
            return self._placeholder_response(text)

        return await self._call_openai(text)

    async def _call_openai(self, text: str) -> ConceptResponse:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=800,
            )
            raw = response.choices[0].message.content.strip()
            data = json.loads(raw)
            return ConceptResponse(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAI returned invalid JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def _placeholder_response(self, text: str) -> ConceptResponse:
        words = text.strip().split()
        topic_guess = " ".join(words[:4]) if len(words) >= 4 else text[:40]
        return ConceptResponse(
            topic=topic_guess,
            key_concepts=[
                "Placeholder concept 1 (set OPENAI_API_KEY to enable AI)",
                "Placeholder concept 2",
                "Placeholder concept 3",
            ],
            examples=[
                "Placeholder example 1",
                "Placeholder example 2",
            ],
        )