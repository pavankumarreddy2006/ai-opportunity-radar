from app.schemas.signal import SignalResponse
from app.services.image_service import category_fallback_image, first_payload_image


def to_signal_response(signal) -> SignalResponse:
    image_url = first_payload_image(signal.raw_news.raw_payload) or category_fallback_image(signal.category)
    return SignalResponse(
        id=signal.id,
        category=signal.category,
        importance_score=signal.importance_score,
        opportunity_score=signal.opportunity_score,
        trend_score=round(signal.trend_velocity * 100),
        action_recommendation=signal.action_recommendation,
        created_at=signal.created_at,
        raw_title=signal.raw_news.title,
        source=signal.raw_news.source,
        link=signal.raw_news.link,
        tags=signal.raw_news.tags,
        published_at=signal.raw_news.published_at,
        image_url=image_url,
        image_alt=f"{signal.category} news image for {signal.raw_news.title}",
        summary=signal.summary,
    )
