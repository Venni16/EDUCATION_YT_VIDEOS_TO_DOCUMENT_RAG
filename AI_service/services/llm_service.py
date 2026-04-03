"""
LLM Service — HuggingFace Inference API
Uses huggingface_hub InferenceClient to call Mistral-7B-Instruct-v0.3
(or any other HF-hosted chat model) via the free serverless API.
"""

import os
import time
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

# Singleton client
_client: InferenceClient | None = None


def get_client() -> InferenceClient:
    global _client
    if _client is None:
        if not HF_TOKEN:
            raise RuntimeError(
                "HF_TOKEN is not set. Please set it in your .env file. "
                "Get your token at https://huggingface.co/settings/tokens"
            )
        logger.info(f"Initializing HuggingFace InferenceClient with model: {HF_MODEL}")
        _client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)
    return _client


def call_llm(prompt: str, max_tokens: int = 1024, temperature: float = 0.4) -> str:
    """
    Call the HuggingFace Inference API with retry logic.

    Args:
        prompt: The user prompt to send.
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature (lower = more focused).

    Returns:
        Generated text string.
    """
    client = get_client()
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"LLM call attempt {attempt}/{MAX_RETRIES} (max_tokens={max_tokens})")
            response = client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            result = response.choices[0].message.content.strip()
            logger.info(f"LLM responded with {len(result)} chars")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"LLM call attempt {attempt} failed: {error_msg}")

            # Model loading (cold start) — wait longer
            if "loading" in error_msg.lower() or "503" in error_msg:
                wait = 20
                logger.info(f"Model is loading (cold start). Waiting {wait}s...")
                time.sleep(wait)
            elif attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                raise RuntimeError(
                    f"HuggingFace API failed after {MAX_RETRIES} attempts: {error_msg}"
                )

    raise RuntimeError("LLM call failed unexpectedly.")


def call_llm_for_list(prompt: str, max_tokens: int = 512) -> list[str]:
    """
    Call LLM and parse response as a bullet-pointed list.
    Returns list of strings (one per non-empty line).
    """
    raw = call_llm(prompt, max_tokens=max_tokens, temperature=0.3)
    lines = []
    for line in raw.splitlines():
        line = line.strip().lstrip("•-*1234567890. ").strip()
        if line and len(line) > 3:
            lines.append(line)
    return lines
