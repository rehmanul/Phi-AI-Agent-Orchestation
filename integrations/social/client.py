"""
Social Media Integration

Provides unified access to social media APIs for monitoring and posting.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel, Field

from core.config import settings

logger = structlog.get_logger()


# =============================================================================
# Models
# =============================================================================

class SocialPost(BaseModel):
    """Represents a social media post."""
    
    platform: str  # twitter, reddit, facebook
    post_id: str
    author: str
    author_id: Optional[str] = None
    content: str
    url: Optional[str] = None
    
    # Engagement
    likes: int = 0
    shares: int = 0
    comments: int = 0
    
    # Metadata
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    
    # Platform-specific
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Twitter/X Client
# =============================================================================

class TwitterClient:
    """
    Client for Twitter/X API v2.
    
    Provides methods for searching tweets, monitoring hashtags,
    and posting content.
    """
    
    def __init__(self):
        self.bearer_token = settings.twitter_bearer_token
        self.api_key = settings.twitter_api_key
        self.api_secret = settings.twitter_api_secret
        self.access_token = settings.twitter_access_token
        self.access_secret = settings.twitter_access_secret
        
        self._client = None
        self._initialized = False
        
        if not self.bearer_token:
            logger.warning("Twitter bearer token not configured")
    
    async def _ensure_initialized(self) -> None:
        """Initialize the Twitter client."""
        if self._initialized:
            return
        
        try:
            import tweepy
            
            if self.bearer_token:
                self._client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                    wait_on_rate_limit=True,
                )
                self._initialized = True
                logger.info("Twitter client initialized")
            else:
                logger.warning("Twitter client not initialized - no credentials")
        except ImportError:
            logger.error("tweepy not installed")
            raise
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[SocialPost]:
        """
        Search for tweets matching a query.
        
        Args:
            query: Search query (supports Twitter search operators)
            max_results: Maximum tweets to return (10-100)
            start_time: Oldest tweet date
            end_time: Newest tweet date
        
        Returns:
            List of matching tweets
        """
        await self._ensure_initialized()
        
        if not self._client:
            logger.warning("Twitter client not available")
            return []
        
        try:
            tweets = self._client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time,
                end_time=end_time,
                tweet_fields=["created_at", "public_metrics", "entities", "author_id"],
                expansions=["author_id"],
                user_fields=["username", "name"],
            )
            
            if not tweets.data:
                return []
            
            # Build user lookup
            users = {}
            if tweets.includes and "users" in tweets.includes:
                for user in tweets.includes["users"]:
                    users[user.id] = user.username
            
            posts = []
            for tweet in tweets.data:
                hashtags = []
                mentions = []
                
                if hasattr(tweet, "entities") and tweet.entities:
                    if "hashtags" in tweet.entities:
                        hashtags = [h["tag"] for h in tweet.entities["hashtags"]]
                    if "mentions" in tweet.entities:
                        mentions = [m["username"] for m in tweet.entities["mentions"]]
                
                metrics = tweet.public_metrics or {}
                
                posts.append(SocialPost(
                    platform="twitter",
                    post_id=str(tweet.id),
                    author=users.get(tweet.author_id, "unknown"),
                    author_id=str(tweet.author_id) if tweet.author_id else None,
                    content=tweet.text,
                    url=f"https://twitter.com/i/web/status/{tweet.id}",
                    likes=metrics.get("like_count", 0),
                    shares=metrics.get("retweet_count", 0),
                    comments=metrics.get("reply_count", 0),
                    hashtags=hashtags,
                    mentions=mentions,
                    created_at=tweet.created_at,
                ))
            
            return posts
        except Exception as e:
            logger.error("Twitter search failed", error=str(e))
            raise
    
    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 100,
    ) -> List[SocialPost]:
        """Get recent tweets from a specific user."""
        await self._ensure_initialized()
        
        if not self._client:
            return []
        
        try:
            # Get user ID first
            user = self._client.get_user(username=username)
            if not user.data:
                return []
            
            user_id = user.data.id
            
            tweets = self._client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "entities"],
            )
            
            if not tweets.data:
                return []
            
            posts = []
            for tweet in tweets.data:
                hashtags = []
                if hasattr(tweet, "entities") and tweet.entities:
                    if "hashtags" in tweet.entities:
                        hashtags = [h["tag"] for h in tweet.entities["hashtags"]]
                
                metrics = tweet.public_metrics or {}
                
                posts.append(SocialPost(
                    platform="twitter",
                    post_id=str(tweet.id),
                    author=username,
                    author_id=str(user_id),
                    content=tweet.text,
                    url=f"https://twitter.com/{username}/status/{tweet.id}",
                    likes=metrics.get("like_count", 0),
                    shares=metrics.get("retweet_count", 0),
                    comments=metrics.get("reply_count", 0),
                    hashtags=hashtags,
                    created_at=tweet.created_at,
                ))
            
            return posts
        except Exception as e:
            logger.error("Failed to get user tweets", username=username, error=str(e))
            raise
    
    async def post_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        """
        Post a tweet.
        
        Args:
            text: Tweet text (max 280 characters)
            reply_to: Tweet ID to reply to
        
        Returns:
            Tweet ID if successful
        """
        await self._ensure_initialized()
        
        if not self._client:
            logger.warning("Twitter client not available for posting")
            return None
        
        try:
            response = self._client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to,
            )
            
            if response.data:
                tweet_id = response.data["id"]
                logger.info("Tweet posted", tweet_id=tweet_id)
                return tweet_id
            
            return None
        except Exception as e:
            logger.error("Failed to post tweet", error=str(e))
            raise


# =============================================================================
# Reddit Client
# =============================================================================

class RedditClient:
    """
    Client for Reddit API using PRAW.
    
    Provides methods for monitoring subreddits and discussions.
    """
    
    def __init__(self):
        self.client_id = settings.reddit_client_id
        self.client_secret = settings.reddit_client_secret
        self.user_agent = settings.reddit_user_agent
        
        self._reddit = None
        self._initialized = False
        
        if not self.client_id:
            logger.warning("Reddit credentials not configured")
    
    async def _ensure_initialized(self) -> None:
        """Initialize the Reddit client."""
        if self._initialized:
            return
        
        try:
            import praw
            
            if self.client_id and self.client_secret:
                self._reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                )
                self._initialized = True
                logger.info("Reddit client initialized")
            else:
                logger.warning("Reddit client not initialized - no credentials")
        except ImportError:
            logger.error("praw not installed")
            raise
    
    async def search_posts(
        self,
        query: str,
        subreddit: Optional[str] = None,
        limit: int = 100,
        time_filter: str = "week",
    ) -> List[SocialPost]:
        """
        Search Reddit posts.
        
        Args:
            query: Search query
            subreddit: Specific subreddit or None for all
            limit: Maximum posts to return
            time_filter: all, day, hour, month, week, year
        
        Returns:
            List of matching posts
        """
        await self._ensure_initialized()
        
        if not self._reddit:
            logger.warning("Reddit client not available")
            return []
        
        try:
            if subreddit:
                sub = self._reddit.subreddit(subreddit)
                results = sub.search(query, limit=limit, time_filter=time_filter)
            else:
                results = self._reddit.subreddit("all").search(
                    query, limit=limit, time_filter=time_filter
                )
            
            posts = []
            for submission in results:
                posts.append(SocialPost(
                    platform="reddit",
                    post_id=submission.id,
                    author=str(submission.author) if submission.author else "[deleted]",
                    content=f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title,
                    url=f"https://reddit.com{submission.permalink}",
                    likes=submission.score,
                    comments=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc),
                    metadata={
                        "subreddit": str(submission.subreddit),
                        "upvote_ratio": submission.upvote_ratio,
                        "is_self": submission.is_self,
                        "flair": submission.link_flair_text,
                    },
                ))
            
            return posts
        except Exception as e:
            logger.error("Reddit search failed", error=str(e))
            raise
    
    async def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = "hot",
        limit: int = 100,
    ) -> List[SocialPost]:
        """
        Get posts from a subreddit.
        
        Args:
            subreddit: Subreddit name
            sort: hot, new, top, rising
            limit: Maximum posts to return
        
        Returns:
            List of posts
        """
        await self._ensure_initialized()
        
        if not self._reddit:
            return []
        
        try:
            sub = self._reddit.subreddit(subreddit)
            
            if sort == "hot":
                results = sub.hot(limit=limit)
            elif sort == "new":
                results = sub.new(limit=limit)
            elif sort == "top":
                results = sub.top(limit=limit, time_filter="week")
            elif sort == "rising":
                results = sub.rising(limit=limit)
            else:
                results = sub.hot(limit=limit)
            
            posts = []
            for submission in results:
                posts.append(SocialPost(
                    platform="reddit",
                    post_id=submission.id,
                    author=str(submission.author) if submission.author else "[deleted]",
                    content=f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title,
                    url=f"https://reddit.com{submission.permalink}",
                    likes=submission.score,
                    comments=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc),
                    metadata={
                        "subreddit": subreddit,
                        "upvote_ratio": submission.upvote_ratio,
                    },
                ))
            
            return posts
        except Exception as e:
            logger.error("Failed to get subreddit posts", subreddit=subreddit, error=str(e))
            raise


# =============================================================================
# Unified Social Media Monitor
# =============================================================================

class SocialMediaMonitor:
    """
    Unified monitor for all social media platforms.
    """
    
    def __init__(self):
        self._twitter = TwitterClient()
        self._reddit = RedditClient()
    
    async def search_all(
        self,
        query: str,
        limit_per_platform: int = 50,
    ) -> List[SocialPost]:
        """
        Search across all platforms.
        
        Args:
            query: Search query
            limit_per_platform: Max results per platform
        
        Returns:
            Combined list of posts sorted by date
        """
        all_posts = []
        
        # Twitter
        try:
            twitter_posts = await self._twitter.search_tweets(
                query=query,
                max_results=min(limit_per_platform, 100),
            )
            all_posts.extend(twitter_posts)
        except Exception as e:
            logger.warning("Twitter search failed", error=str(e))
        
        # Reddit
        try:
            reddit_posts = await self._reddit.search_posts(
                query=query,
                limit=limit_per_platform,
            )
            all_posts.extend(reddit_posts)
        except Exception as e:
            logger.warning("Reddit search failed", error=str(e))
        
        # Sort by date (newest first)
        all_posts.sort(
            key=lambda p: p.created_at or datetime.min,
            reverse=True,
        )
        
        return all_posts
    
    async def search_advocacy_keywords(
        self,
        keywords: List[str],
    ) -> List[SocialPost]:
        """
        Search for posts matching advocacy campaign keywords.
        
        Args:
            keywords: List of keywords to search
        
        Returns:
            List of relevant posts
        """
        all_posts = []
        
        for keyword in keywords:
            try:
                posts = await self.search_all(keyword, limit_per_platform=20)
                all_posts.extend(posts)
            except Exception as e:
                logger.warning("Search failed for keyword", keyword=keyword, error=str(e))
        
        # Deduplicate by post_id + platform
        seen = set()
        unique = []
        for post in all_posts:
            key = (post.platform, post.post_id)
            if key not in seen:
                seen.add(key)
                unique.append(post)
        
        # Sort by date
        unique.sort(key=lambda p: p.created_at or datetime.min, reverse=True)
        
        return unique


# =============================================================================
# Convenience Functions
# =============================================================================

async def search_wireless_power_social(
    limit_per_platform: int = 50,
) -> List[SocialPost]:
    """
    Search for social media content related to wireless power.
    
    Default use case for the advocacy system.
    """
    keywords = [
        "wireless power",
        "wireless charging",
        '"Wi-Charge"',
        "power over air",
    ]
    
    monitor = SocialMediaMonitor()
    return await monitor.search_advocacy_keywords(keywords)
