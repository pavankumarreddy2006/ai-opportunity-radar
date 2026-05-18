from app.db.session import Base
from app.models.category import Category
from app.models.interest import Interest
from app.models.news import News
from app.models.raw_news import RawNews
from app.models.signal import Signal
from app.models.source import Source
from app.models.summary import Summary
from app.models.trend_score import TrendScore
from app.models.user import User
from app.models.user_preference import UserPreference

__all__ = [
    "Base",
    "User",
    "Interest",
    "UserPreference",
    "Source",
    "Category",
    "News",
    "RawNews",
    "TrendScore",
    "Signal",
    "Summary",
]
