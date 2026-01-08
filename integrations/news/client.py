"""
News Aggregation Integration

Provides unified access to multiple news sources for monitoring.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
import httpx
import structlog
from pydantic import BaseModel, Field

from core.config import settings

logger = structlog.get_logger()


# =============================================================================
# Models
# =============================================================================

class NewsArticle(BaseModel):
    """Represents a news article."""
    
    source: str
    source_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # Metadata
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)


# =============================================================================
# NewsAPI Client
# =============================================================================

class NewsAPIClient:
    """
    Client for NewsAPI.org.
    
    Provides access to news from 80,000+ sources worldwide.
    """
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.newsapi_key
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
        
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        )
    
    async def close(self) -> None:
        await self._client.aclose()
    
    async def _request(
        self,
        endpoint: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make an API request."""
        params["apiKey"] = self.api_key
        
        try:
            response = await self._client.get(endpoint, params=params)
            data = response.json()
            
            if data.get("status") == "error":
                logger.error(
                    "NewsAPI error",
                    code=data.get("code"),
                    message=data.get("message"),
                )
                raise Exception(data.get("message", "Unknown error"))
            
            return data
        except Exception as e:
            logger.error("NewsAPI request failed", error=str(e))
            raise
    
    async def search(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 100,
        page: int = 1,
    ) -> List[NewsArticle]:
        """
        Search all articles.
        
        Args:
            query: Keywords or phrases to search for
            from_date: Oldest article date
            to_date: Newest article date
            language: Language code
            sort_by: relevancy, popularity, or publishedAt
            page_size: Number of results (max 100)
            page: Page number
        
        Returns:
            List of articles
        """
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
        }
        
        if from_date:
            params["from"] = from_date.isoformat()
        if to_date:
            params["to"] = to_date.isoformat()
        
        data = await self._request("/everything", params)
        
        articles = []
        for item in data.get("articles", []):
            try:
                published = None
                if item.get("publishedAt"):
                    try:
                        published = datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass
                
                articles.append(NewsArticle(
                    source=item.get("source", {}).get("name", "Unknown"),
                    source_id=item.get("source", {}).get("id"),
                    title=item.get("title", ""),
                    description=item.get("description"),
                    content=item.get("content"),
                    url=item.get("url", ""),
                    image_url=item.get("urlToImage"),
                    author=item.get("author"),
                    published_at=published,
                ))
            except Exception as e:
                logger.warning("Failed to parse article", error=str(e))
        
        return articles
    
    async def get_top_headlines(
        self,
        query: Optional[str] = None,
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 100,
    ) -> List[NewsArticle]:
        """
        Get top headlines.
        
        Args:
            query: Keywords to search for
            country: Country code
            category: business, technology, science, health, etc.
            page_size: Number of results
        
        Returns:
            List of top headline articles
        """
        params = {
            "country": country,
            "pageSize": page_size,
        }
        
        if query:
            params["q"] = query
        if category:
            params["category"] = category
        
        data = await self._request("/top-headlines", params)
        
        articles = []
        for item in data.get("articles", []):
            try:
                published = None
                if item.get("publishedAt"):
                    try:
                        published = datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass
                
                articles.append(NewsArticle(
                    source=item.get("source", {}).get("name", "Unknown"),
                    source_id=item.get("source", {}).get("id"),
                    title=item.get("title", ""),
                    description=item.get("description"),
                    content=item.get("content"),
                    url=item.get("url", ""),
                    image_url=item.get("urlToImage"),
                    author=item.get("author"),
                    published_at=published,
                    categories=[category] if category else [],
                ))
            except Exception as e:
                logger.warning("Failed to parse article", error=str(e))
        
        return articles
    
    async def __aenter__(self) -> "NewsAPIClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# =============================================================================
# Google News RSS Client
# =============================================================================

class GoogleNewsClient:
    """
    Client for Google News RSS feeds.
    
    Free alternative to NewsAPI with no rate limits.
    """
    
    BASE_URL = "https://news.google.com/rss"
    
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self) -> None:
        await self._client.aclose()
    
    async def search(
        self,
        query: str,
        language: str = "en",
        country: str = "US",
    ) -> List[NewsArticle]:
        """
        Search Google News.
        
        Args:
            query: Search query
            language: Language code
            country: Country code
        
        Returns:
            List of articles
        """
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}/search?q={encoded_query}&hl={language}&gl={country}&ceid={country}:{language}"
        
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            articles = []
            for entry in feed.entries:
                try:
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    # Extract source from title (Google News format: "Title - Source")
                    title = entry.get("title", "")
                    source = "Google News"
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        if len(parts) == 2:
                            title, source = parts
                    
                    articles.append(NewsArticle(
                        source=source,
                        title=title,
                        description=entry.get("summary", ""),
                        url=entry.get("link", ""),
                        published_at=published,
                    ))
                except Exception as e:
                    logger.warning("Failed to parse RSS entry", error=str(e))
            
            return articles
        except Exception as e:
            logger.error("Google News request failed", error=str(e))
            raise
    
    async def get_topic(
        self,
        topic: str,
        language: str = "en",
        country: str = "US",
    ) -> List[NewsArticle]:
        """
        Get articles from a topic feed.
        
        Args:
            topic: Topic ID (TECHNOLOGY, BUSINESS, SCIENCE, HEALTH, etc.)
            language: Language code
            country: Country code
        
        Returns:
            List of articles
        """
        url = f"{self.BASE_URL}/headlines/section/topic/{topic}?hl={language}&gl={country}&ceid={country}:{language}"
        
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            articles = []
            for entry in feed.entries:
                try:
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    title = entry.get("title", "")
                    source = "Google News"
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        if len(parts) == 2:
                            title, source = parts
                    
                    articles.append(NewsArticle(
                        source=source,
                        title=title,
                        description=entry.get("summary", ""),
                        url=entry.get("link", ""),
                        published_at=published,
                        categories=[topic.lower()],
                    ))
                except Exception as e:
                    logger.warning("Failed to parse RSS entry", error=str(e))
            
            return articles
        except Exception as e:
            logger.error("Google News topic request failed", error=str(e))
            raise
    
    async def __aenter__(self) -> "GoogleNewsClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# =============================================================================
# Unified News Aggregator
# =============================================================================

class NewsAggregator:
    """
    Unified news aggregator that combines multiple sources.
    """
    
    def __init__(self):
        self._newsapi = NewsAPIClient() if settings.newsapi_key else None
        self._google = GoogleNewsClient()
    
    async def close(self) -> None:
        if self._newsapi:
            await self._newsapi.close()
        await self._google.close()
    
    async def search(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[NewsArticle]:
        """
        Search for news articles across all sources.
        
        Args:
            query: Search query
            from_date: Oldest article date
            limit: Maximum articles to return
        
        Returns:
            List of deduplicated articles sorted by date
        """
        articles = []
        
        # Try NewsAPI first if available
        if self._newsapi:
            try:
                newsapi_articles = await self._newsapi.search(
                    query=query,
                    from_date=from_date,
                    page_size=min(limit, 100),
                )
                articles.extend(newsapi_articles)
            except Exception as e:
                logger.warning("NewsAPI search failed", error=str(e))
        
        # Always try Google News (free, no rate limits)
        try:
            google_articles = await self._google.search(query)
            articles.extend(google_articles)
        except Exception as e:
            logger.warning("Google News search failed", error=str(e))
        
        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        # Sort by date (newest first)
        unique_articles.sort(
            key=lambda a: a.published_at or datetime.min,
            reverse=True,
        )
        
        return unique_articles[:limit]
    
    async def search_advocacy_keywords(
        self,
        keywords: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[NewsArticle]:
        """
        Search for articles matching advocacy campaign keywords.
        
        Args:
            keywords: List of keywords to search
            from_date: Oldest article date
        
        Returns:
            List of relevant articles
        """
        all_articles = []
        
        for keyword in keywords:
            try:
                articles = await self.search(keyword, from_date=from_date, limit=20)
                all_articles.extend(articles)
            except Exception as e:
                logger.warning("Search failed for keyword", keyword=keyword, error=str(e))
        
        # Deduplicate
        seen_urls = set()
        unique = []
        for article in all_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique.append(article)
        
        # Sort by date
        unique.sort(key=lambda a: a.published_at or datetime.min, reverse=True)
        
        return unique
    
    async def __aenter__(self) -> "NewsAggregator":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def search_wireless_power_news(
    from_date: Optional[datetime] = None,
) -> List[NewsArticle]:
    """
    Search for news related to wireless power/charging.
    
    Default use case for the advocacy system.
    """
    keywords = [
        "wireless power",
        "wireless charging",
        "wireless energy transfer",
        "inductive charging",
        "Wi-Charge",
    ]
    
    async with NewsAggregator() as aggregator:
        return await aggregator.search_advocacy_keywords(keywords, from_date=from_date)
