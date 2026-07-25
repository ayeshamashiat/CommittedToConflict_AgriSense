"""Thin OpenAI API wrapper: chat completion + function-calling, isolated from agent logic.

Every other agent module talks to the LLM only through this class, never
through the `openai` package directly, so the rest of the agent stays
provider-agnostic and testable without a live API key.
"""

import io
import json
import logging

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMClient:
    """Wraps OpenAI chat completions. If no API key is configured, every
    method returns None so callers can fall back to deterministic logic —
    the agent must stay fully functional (Tier 0) without an LLM key."""

    def __init__(self):
        self.model = settings.openai_model
        self._client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 400,
    ) -> str | None:
        """Plain text completion (e.g. for phrasing a clarifying question)."""
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception:
            logger.exception("LLM completion failed; caller should fall back")
            return None

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> dict | None:
        """Completion constrained to return a JSON object (used by the planner
        to pick candidate crops, and the explainer to produce structured
        reasoning). Returns a parsed dict, or None on any failure."""
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content) if content else None
        except Exception:
            logger.exception("LLM JSON completion failed; caller should fall back")
            return None

    def classify_image_json(
        self,
        system_prompt: str,
        user_prompt: str,
        image_base64: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> dict | None:
        """Tier 2 plant disease detection: sends an image to a vision-capable
        OpenAI model (gpt-4o-mini and later support image inputs) alongside a
        text prompt, constrained to return JSON. There is no offline/no-key
        fallback for this one — unlike every other tool in this app, real
        image classification genuinely requires a vision model; callers must
        surface that limitation honestly rather than fake a result."""
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            },
                        ],
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content) if content else None
        except Exception:
            logger.exception("LLM image classification failed")
            return None

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language: str | None = None,
    ) -> str | None:
        """Tier 2 voice input: speech-to-text via OpenAI's Whisper model.
        `language` should be an ISO-639-1 code (e.g. "en", "bn") — passing it
        is optional (Whisper auto-detects) but pins the guess to the app's
        current UI language, which resolves ambiguity on short recordings."""
        if not self._client:
            return None
        try:
            buffer = io.BytesIO(audio_bytes)
            buffer.name = filename
            response = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer,
                language=language,
            )
            return response.text
        except Exception:
            logger.exception("Whisper transcription failed")
            return None

    def call_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 600,
    ):
        """OpenAI function-calling: lets the model decide which tool(s) to
        invoke and with what arguments. Returns the raw ChatCompletionMessage
        (with .tool_calls / .content) or None if no LLM is configured."""
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message
        except Exception:
            logger.exception("LLM tool-call request failed; caller should fall back")
            return None
