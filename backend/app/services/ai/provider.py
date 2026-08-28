import json
import logging
import re
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import Settings
from app.core.exceptions import LLMProviderError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    async def generate_text(self, system: str, user: str, temperature: float = 0.2) -> str:
        ...

    async def generate_json(self, system: str, user: str, schema: type[T], temperature: float = 0.1) -> T:
        prompt = (
            f"{user}\n\nRespond with valid JSON only matching this schema. "
            f"No markdown, no explanation."
        )
        text = await self.generate_text(system, prompt, temperature)
        data = _extract_json(text)
        return schema.model_validate(data)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise LLMProviderError("Failed to parse LLM JSON response")


class GroqProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.models = settings.groq_model_candidates

    async def generate_text(self, system: str, user: str, temperature: float = 0.2) -> str:
        if not self.settings.groq_api_key:
            raise LLMProviderError("GROQ_API_KEY not configured")
        from groq import AsyncGroq

        client = AsyncGroq(api_key=self.settings.groq_api_key)
        last_error: Exception | None = None

        for model in self.models:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    max_tokens=4096,
                )
                if model != self.models[0]:
                    logger.info("Groq request succeeded with fallback model: %s", model)
                return response.choices[0].message.content or ""
            except Exception as e:
                last_error = e
                err = str(e).lower()
                if "404" in str(e) or "does not exist" in err or "decommissioned" in err:
                    logger.warning("Groq model %s unavailable, trying next: %s", model, e)
                    continue
                logger.exception("Groq API error on model %s", model)
                raise LLMProviderError(f"Groq API error: {e}") from e

        logger.exception("All Groq models failed")
        raise LLMProviderError(f"Groq API error: {last_error}") from last_error


class GeminiProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.gemini_model

    async def generate_text(self, system: str, user: str, temperature: float = 0.2) -> str:
        if not self.settings.gemini_api_key:
            raise LLMProviderError("GEMINI_API_KEY not configured")
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.gemini_api_key)
            model = genai.GenerativeModel(
                self.model,
                system_instruction=system,
                generation_config={"temperature": temperature, "max_output_tokens": 4096},
            )
            response = await model.generate_content_async(user)
            return response.text or ""
        except Exception as e:
            logger.exception("Gemini API error")
            raise LLMProviderError(f"Gemini API error: {e}") from e


class FallbackProvider(LLMProvider):
    """Rule-based fallback when no API key is configured."""

    async def generate_text(self, system: str, user: str, temperature: float = 0.2) -> str:
        # Extract the research question from the planner prompt when possible
        question = user
        if "Question:" in user:
            question = user.split("Question:", 1)[1].strip().split("\n")[0].strip()

        return json.dumps({
            "population": "",
            "intervention": "",
            "comparison": "",
            "outcomes": [],
            "study_types": [],
            "search_queries": [question],
            "executive_summary": (
                "Evidence synthesis requires an LLM API key. "
                "Configure GROQ_API_KEY (free at groq.com) or GEMINI_API_KEY. "
                "Papers were retrieved and ranked successfully."
            ),
            "key_findings": ["Literature search completed. Configure LLM for full synthesis."],
            "evidence_strength": "Unknown",
            "evidence_strength_reason": "LLM not configured for synthesis.",
            "limitations": ["Automated synthesis unavailable without API key."],
            "research_gaps": ["Full evidence synthesis pending LLM configuration."],
            "claims": [],
        })


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "groq" and settings.groq_api_key:
        return GroqProvider(settings)
    if provider == "gemini" and settings.gemini_api_key:
        return GeminiProvider(settings)
    if settings.groq_api_key:
        return GroqProvider(settings)
    if settings.gemini_api_key:
        return GeminiProvider(settings)
    logger.warning("No LLM API key configured, using fallback provider")
    return FallbackProvider()
