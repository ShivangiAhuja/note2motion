import json
import logging
from typing import List

from app.models.schemas import ConceptResponse, Scene, ScenePlanResponse
from app.utils.config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert educational video scriptwriter. Given structured concept data, \
produce a scene-by-scene breakdown for a clear, engaging educational video.

Respond ONLY with a valid JSON object in this exact format:
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_title": "<short title>",
      "narration": "<what the narrator says in this scene>",
      "visual_type": "<one of: diagram | text_slide | example | code_demo>",
      "duration": <integer seconds>
    }
  ]
}

Guidelines:
- Start with an intro scene that states the topic and why it matters.
- Dedicate one scene per key concept (use text_slide or diagram as appropriate).
- Include at least one scene per example (use example or code_demo as appropriate).
- End with a summary/recap scene.
- Narration should be natural, spoken-word style (1–3 sentences per scene).
- Duration: intro/outro ~15s, concept scenes ~20–30s, example scenes ~25–35s.
- visual_type rules:
    diagram      → abstract relationships, processes, cycles
    text_slide   → definitions, lists of points, terminology
    example      → real-world scenarios, analogies
    code_demo    → algorithms, syntax, programming concepts
- No markdown, no extra text — pure JSON only."""


class SceneAgent:
    async def plan(self, concept: ConceptResponse) -> ScenePlanResponse:
        if config.USE_PLACEHOLDER:
            logger.warning("OPENAI_API_KEY not set — returning placeholder scene plan.")
            return self._placeholder_response(concept)

        return await self._call_openai(concept)

    async def _call_openai(self, concept: ConceptResponse) -> ScenePlanResponse:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

            user_message = (
                f"Topic: {concept.topic}\n"
                f"Key Concepts: {json.dumps(concept.key_concepts)}\n"
                f"Examples: {json.dumps(concept.examples)}"
            )

            response = await client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.4,
                max_tokens=1600,
            )

            raw = response.choices[0].message.content.strip()
            data = json.loads(raw)
            scenes: List[Scene] = [Scene(**s) for s in data["scenes"]]
            return ScenePlanResponse(
                topic=concept.topic,
                total_scenes=len(scenes),
                estimated_total_duration=sum(s.duration for s in scenes),
                scenes=scenes,
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAI returned invalid JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def _placeholder_response(self, concept: ConceptResponse) -> ScenePlanResponse:
        scenes = [
            Scene(
                scene_number=1,
                scene_title=f"Introduction to {concept.topic}",
                narration=f"Welcome! In this video, we'll explore {concept.topic} and why it matters.",
                visual_type="text_slide",
                duration=15,
            )
        ]

        for i, kc in enumerate(concept.key_concepts, start=2):
            scenes.append(
                Scene(
                    scene_number=i,
                    scene_title=kc,
                    narration=f"Let's look at a key concept: {kc}.",
                    visual_type="diagram",
                    duration=25,
                )
            )

        offset = len(scenes) + 1
        for j, ex in enumerate(concept.examples, start=offset):
            scenes.append(
                Scene(
                    scene_number=j,
                    scene_title=f"Example: {ex[:40]}",
                    narration=f"Here's a concrete example to make this tangible: {ex}",
                    visual_type="example",
                    duration=30,
                )
            )

        scenes.append(
            Scene(
                scene_number=len(scenes) + 1,
                scene_title="Recap & Key Takeaways",
                narration=(
                    f"To summarise: we covered {len(concept.key_concepts)} core concepts "
                    f"around {concept.topic}. Keep these ideas in mind as you explore further."
                ),
                visual_type="text_slide",
                duration=20,
            )
        )

        return ScenePlanResponse(
            topic=concept.topic,
            total_scenes=len(scenes),
            estimated_total_duration=sum(s.duration for s in scenes),
            scenes=scenes,
        )