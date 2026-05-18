from fastapi import APIRouter

from app.api.routes import auth, dashboard, health, preferences, signals, trending, update_news

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(trending.router, prefix="/trending", tags=["trending"])
api_router.include_router(update_news.router, prefix="/update-news", tags=["update-news"])
