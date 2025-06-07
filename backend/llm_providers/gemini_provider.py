import httpx
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

class GeminiProviderError(Exception):
    pass

class GeminiProvider:
    def __init__(
        self,
        model_name: str,
        api_key: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.95,
        top_k: int = 40,
        stop_sequences: Optional[List[str]] = None,
        timeout: int = 60,
        safety_settings: Optional[List[dict]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        backend: Optional[str] = "google",
        **kwargs
    ):
        self.model_name = model_name
        self.api_key = api_key
        if not self.api_key:
            raise GeminiProviderError("Missing Gemini API key! Set in gemini_config YAML.")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.stop_sequences = stop_sequences or []
        self.timeout = timeout
        self.safety_settings = safety_settings or []
        self.metadata = metadata or {}
        self.backend = backend

    async def generate(self, prompt: str, **kwargs) -> str:
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
            "maxOutputTokens": kwargs.get("max_tokens", self.max_tokens),
            "topP": kwargs.get("top_p", self.top_p),
            "topK": kwargs.get("top_k", self.top_k),
            "stopSequences": kwargs.get("stop_sequences", self.stop_sequences)
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": generation_config,
            "safetySettings": self.safety_settings,
        }
        if self.metadata:
            logger.info(f"[GeminiProvider] Meta: {self.metadata}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise GeminiProviderError(f"No candidates in Gemini response: {data}")
                result = candidates[0]['content']['parts'][0]['text']
                return result
            except Exception as e:
                logger.error(f"[GeminiProvider] Error calling Gemini: {e}")
                raise GeminiProviderError(f"Gemini API error: {e}")