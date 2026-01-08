"""News integration exports."""

from integrations.news.client import (
    GoogleNewsClient,
    NewsAggregator,
    NewsAPIClient,
    NewsArticle,
    search_wireless_power_news,
)

__all__ = [
    "NewsAPIClient",
    "GoogleNewsClient",
    "NewsAggregator",
    "NewsArticle",
    "search_wireless_power_news",
]
