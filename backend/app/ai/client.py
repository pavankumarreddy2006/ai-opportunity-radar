from openai import OpenAI

from app.core.settings import get_settings


def get_openai_client() -> OpenAI | None:
    settings = get_settings()

    if settings.openai_api_key:
        return OpenAI(api_key=settings.openai_api_key)

    return None


def get_openrouter_client() -> OpenAI | None:
    settings = get_settings()

    if settings.openrouter_api_key:
        return OpenAI(api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url)

    return None


def get_ai_client() -> OpenAI | None:
    return get_openai_client() or get_openrouter_client()
