"""
Platform fetchers for BookmarkHub.
Each fetcher pulls bookmarks from a specific platform.
"""

import json
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from bs4 import BeautifulSoup


class BaseFetcher(ABC):
    """Base class for all bookmark fetchers."""

    name: str = "base"

    @abstractmethod
    def fetch(self, **kwargs) -> list[dict]:
        """Fetch bookmarks from the platform. Returns list of bookmark dicts."""
        ...


class HackerNewsFetcher(BaseFetcher):
    """Fetch top stories and saved items from Hacker News."""

    name = "hackernews"

    def fetch(self, limit: int = 30, **kwargs) -> list[dict]:
        """Fetch top HN stories via the public Algolia API (no auth required)."""
        bookmarks = []
        url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={limit}"
        try:
            resp = httpx.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for hit in data.get("hits", []):
                story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                bookmarks.append({
                    "url": story_url,
                    "title": hit.get("title", ""),
                    "description": f"HN Score: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                    "source": "hackernews",
                    "tags": ["hackernews"],
                })
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to fetch Hacker News: {e}") from e
        return bookmarks


class RedditFetcher(BaseFetcher):
    """Fetch saved posts from Reddit via JSON feed (public, no auth for public subreddits)."""

    name = "reddit"

    def fetch(self, subreddit: str = "popular", limit: int = 30, **kwargs) -> list[dict]:
        """Fetch top posts from a subreddit via public JSON endpoint."""
        bookmarks = []
        url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
        headers = {"User-Agent": "BookmarkHub/1.0"}
        try:
            resp = httpx.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for child in data.get("data", {}).get("children", []):
                post = child["data"]
                post_url = f"https://reddit.com{post.get('permalink', '')}"
                bookmarks.append({
                    "url": post_url,
                    "title": post.get("title", ""),
                    "description": f"r/{post.get('subreddit')} | Score: {post.get('score', 0)} | 💬 {post.get('num_comments', 0)}",
                    "source": "reddit",
                    "tags": ["reddit", post.get("subreddit", "")],
                })
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to fetch Reddit: {e}") from e
        return bookmarks


class GitHubTrendingFetcher(BaseFetcher):
    """Fetch trending repositories from GitHub."""

    name = "github"

    def fetch(self, language: str = "", since: str = "daily", limit: int = 30, **kwargs) -> list[dict]:
        """Scrape GitHub Trending page for trending repos."""
        bookmarks = []
        lang_path = f"/{language}" if language else ""
        url = f"https://github.com/trending{lang_path}?since={since}"
        headers = {"User-Agent": "BookmarkHub/1.0"}
        try:
            resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.select("article.Box-row")
            for article in articles[:limit]:
                h2 = article.select_one("h2 a")
                if not h2:
                    continue
                repo_path = h2.get("href", "").strip("/")
                repo_url = f"https://github.com/{repo_path}"
                desc_el = article.select_one("p")
                description = desc_el.get_text(strip=True) if desc_el else ""
                # Stars count
                stars_el = article.select_one("a.Link--muted.d-inline-block.mr-3")
                stars = stars_el.get_text(strip=True).replace(",", "") if stars_el else "0"
                bookmarks.append({
                    "url": repo_url,
                    "title": repo_path,
                    "description": f"⭐ {stars} | {description}",
                    "source": "github",
                    "tags": ["github", "trending"] + ([language] if language else []),
                })
        except (httpx.HTTPError, Exception) as e:
            raise RuntimeError(f"Failed to fetch GitHub Trending: {e}") from e
        return bookmarks


class LobstersFetcher(BaseFetcher):
    """Fetch top stories from Lobste.rs."""

    name = "lobsters"

    def fetch(self, limit: int = 30, **kwargs) -> list[dict]:
        """Fetch top Lobste.rs stories via JSON API."""
        bookmarks = []
        url = "https://lobste.rs/hottest.json"
        try:
            resp = httpx.get(url, timeout=15)
            resp.raise_for_status()
            stories = resp.json()
            for story in stories[:limit]:
                bookmarks.append({
                    "url": story.get("url", f"https://lobste.rs/s/{story.get('short_id', '')}"),
                    "title": story.get("title", ""),
                    "description": f"Lobsters | Score: {story.get('score', 0)} | 💬 {story.get('comment_count', 0)} | Tags: {', '.join(story.get('tags', []))}",
                    "source": "lobsters",
                    "tags": ["lobsters"] + story.get("tags", []),
                })
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to fetch Lobste.rs: {e}") from e
        return bookmarks


FETCHERS: dict[str, type[BaseFetcher]] = {
    "hackernews": HackerNewsFetcher,
    "reddit": RedditFetcher,
    "github": GitHubTrendingFetcher,
    "lobsters": LobstersFetcher,
}


def get_fetcher(name: str) -> BaseFetcher:
    """Get a fetcher instance by platform name."""
    if name not in FETCHERS:
        raise ValueError(f"Unknown platform: {name}. Available: {', '.join(FETCHERS.keys())}")
    return FETCHERS[name]()
