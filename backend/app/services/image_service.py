from functools import lru_cache
from html import unescape
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

CATEGORY_FALLBACK_IMAGES = {
    "ai agents": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
    "model releases": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
    "research breakthroughs": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&w=1200&q=80",
    "open source ai": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?auto=format&fit=crop&w=1200&q=80",
    "developer tools": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80",
    "ai infrastructure": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    "startup and funding": "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=80",
    "policy and safety": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1200&q=80",
    "finance": "https://images.unsplash.com/photo-1642543348745-03b1219733d9?auto=format&fit=crop&w=1200&q=80",
    "crypto": "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=1200&q=80",
}

GENERIC_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80"


def category_fallback_image(category: str | None) -> str:
    key = (category or "").strip().lower()
    return CATEGORY_FALLBACK_IMAGES.get(key, GENERIC_FALLBACK_IMAGE)


def first_payload_image(payload: dict | None) -> str | None:
    if not payload:
        return None
    candidates = [
        payload.get("image_url"),
        payload.get("image"),
        payload.get("thumbnail"),
        payload.get("og_image"),
        payload.get("urlToImage"),
    ]
    media = payload.get("media")
    if isinstance(media, dict):
        candidates.extend([media.get("thumbnail"), media.get("content"), media.get("url")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith(("http://", "https://")):
            return candidate
    return None


@lru_cache(maxsize=512)
def fetch_og_image(url: str) -> str | None:
    try:
        with httpx.Client(timeout=4, follow_redirects=True) as client:
            response = client.get(url, headers={"User-Agent": "ai-opportunity-radar/1.0"})
            response.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(response.text[:200_000], "html.parser")
    selectors = [
        ("property", "og:image"),
        ("name", "twitter:image"),
        ("property", "og:image:secure_url"),
    ]
    for attr, value in selectors:
        tag = soup.find("meta", attrs={attr: value})
        content = tag.get("content") if tag else None
        if isinstance(content, str) and content.strip():
            image_url = urljoin(url, unescape(content.strip()))
            if image_url.startswith(("http://", "https://")):
                return image_url
    return None


def resolve_image_url(link: str, category: str | None, payload: dict | None) -> str:
    return first_payload_image(payload) or fetch_og_image(link) or category_fallback_image(category)
