import hashlib
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, urlunparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.logging import get_logger

logger = get_logger(__name__)

AI_KEYWORDS = {
    "ai",
    "agent",
    "agents",
    "agi",
    "anthropic",
    "chatgpt",
    "claude",
    "copilot",
    "diffusion",
    "embedding",
    "fine-tuning",
    "frontier model",
    "gemini",
    "generative",
    "gpt",
    "inference",
    "llama",
    "llm",
    "machine learning",
    "mcp",
    "model",
    "multimodal",
    "openai",
    "rag",
    "reasoning model",
    "sora",
    "transformer",
    "vision model",
}


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    cleaned = parsed._replace(query="", fragment="")
    return urlunparse(cleaned).rstrip("/")


def build_dedupe_key(title: str, link: str) -> str:
    normalized = f"{title.strip().lower()}::{normalize_url(link).lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9\-\+]+", text.lower())


def is_ai_related(text: str) -> bool:
    tokens = set(tokenize(text))
    normalized = " ".join(tokens)
    for keyword in AI_KEYWORDS:
        if " " in keyword:
            if keyword in text.lower():
                return True
            continue
        if keyword in tokens:
            return True
    return False


def parse_http_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        return None


def parse_int(value: str | int | float | None) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    digits = re.sub(r"[^0-9]", "", value)
    return int(digits) if digits else 0


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def resilient_get(client: httpx.Client, url: str) -> httpx.Response:
    response = client.get(url)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        sleep_seconds = int(retry_after) if retry_after and retry_after.isdigit() else 3
        logger.info("Rate limited by %s; sleeping for %s seconds", urlparse(url).netloc, sleep_seconds)
        time.sleep(min(sleep_seconds, 10))
    response.raise_for_status()
    return response
