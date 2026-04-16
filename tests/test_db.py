"""Unit tests for BookmarkHub database layer."""

import json
import tempfile
from pathlib import Path

import pytest

from bookmarkhub.db import BookmarkDB, _auto_tag


@pytest.fixture
def db(tmp_path):
    """Create a temporary BookmarkDB for testing."""
    db_path = tmp_path / "test.db"
    database = BookmarkDB(db_path=db_path)
    yield database
    database.close()


class TestAutoTag:
    def test_python_tag(self):
        tags = _auto_tag("Python Tutorial", "Learn python programming")
        assert "programming" in tags

    def test_ai_tag(self):
        tags = _auto_tag("GPT-4 Released", "New AI model from OpenAI")
        assert "ai" in tags

    def test_no_tag(self):
        tags = _auto_tag("Cooking Recipe", "How to make pasta")
        assert tags == []

    def test_multiple_tags(self):
        tags = _auto_tag("Docker Kubernetes Guide", "DevOps best practices")
        assert "devops" in tags


class TestBookmarkDB:
    def test_add_bookmark(self, db):
        bid = db.add_bookmark(
            url="https://example.com",
            title="Example",
            description="Test bookmark",
            source="manual",
        )
        assert bid > 0

    def test_add_duplicate_url_same_source(self, db):
        bid1 = db.add_bookmark(url="https://example.com", source="manual")
        bid2 = db.add_bookmark(url="https://example.com", source="manual")
        # Same URL + source should upsert, not error
        assert bid2 > 0

    def test_add_same_url_different_source(self, db):
        bid1 = db.add_bookmark(url="https://example.com", source="manual")
        bid2 = db.add_bookmark(url="https://example.com", source="hackernews")
        assert bid1 > 0
        assert bid2 > 0

    def test_search(self, db):
        db.add_bookmark(url="https://python.org", title="Python Official", source="manual")
        db.add_bookmark(url="https://rust-lang.org", title="Rust Language", source="manual")
        results = db.search("Python")
        assert len(results) == 1
        assert results[0]["title"] == "Python Official"

    def test_list_bookmarks(self, db):
        db.add_bookmark(url="https://a.com", title="A", source="manual")
        db.add_bookmark(url="https://b.com", title="B", source="hackernews")
        results = db.list_bookmarks(source="manual")
        assert len(results) == 1
        assert results[0]["title"] == "A"

    def test_list_by_tag(self, db):
        db.add_bookmark(url="https://a.com", title="AI News", source="manual", tags=["ai", "news"])
        db.add_bookmark(url="https://b.com", title="Cooking", source="manual", tags=["food"])
        results = db.list_bookmarks(tag="ai")
        assert len(results) == 1
        assert results[0]["title"] == "AI News"

    def test_stats(self, db):
        db.add_bookmark(url="https://a.com", title="A", source="manual")
        db.add_bookmark(url="https://b.com", title="B", source="hackernews")
        stats = db.get_stats()
        assert stats["total"] == 2
        assert "manual" in stats["by_source"]
        assert "hackernews" in stats["by_source"]

    def test_delete_bookmark(self, db):
        bid = db.add_bookmark(url="https://example.com", title="Delete me", source="manual")
        assert db.delete_bookmark(bid) is True
        assert db.delete_bookmark(9999) is False

    def test_add_bookmarks_batch(self, db):
        bookmarks = [
            {"url": "https://a.com", "title": "A", "source": "manual"},
            {"url": "https://b.com", "title": "B", "source": "manual"},
            {"url": "https://c.com", "title": "C", "source": "reddit"},
        ]
        added = db.add_bookmarks_batch(bookmarks)
        assert added == 3
