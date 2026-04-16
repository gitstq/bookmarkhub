"""Unit tests for BookmarkHub exporter."""

import json
import zipfile
from pathlib import Path

import pytest

from bookmarkhub.exporter import (
    export_bookmarks,
    export_epub,
    export_html,
    export_json,
    export_markdown,
)

SAMPLE_BOOKMARKS = [
    {
        "id": 1,
        "url": "https://example.com/python",
        "title": "Python Tutorial",
        "description": "Learn Python",
        "source": "hackernews",
        "tags": '["programming", "python"]',
        "created_at": "2026-04-16T10:00:00",
        "synced_at": "2026-04-16T10:00:00",
    },
    {
        "id": 2,
        "url": "https://example.com/rust",
        "title": "Rust Guide",
        "description": "Learn Rust",
        "source": "reddit",
        "tags": '["programming", "rust"]',
        "created_at": "2026-04-16T09:00:00",
        "synced_at": "2026-04-16T09:00:00",
    },
]


class TestExportMarkdown:
    def test_export_creates_file(self, tmp_path):
        path = str(tmp_path / "test.md")
        result = export_markdown(SAMPLE_BOOKMARKS, path)
        assert Path(result).exists()
        content = Path(result).read_text(encoding="utf-8")
        assert "Python Tutorial" in content
        assert "Rust Guide" in content
        assert "Hackernews" in content

    def test_export_includes_source_groups(self, tmp_path):
        path = str(tmp_path / "test.md")
        export_markdown(SAMPLE_BOOKMARKS, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "Hackernews" in content
        assert "Reddit" in content


class TestExportJSON:
    def test_export_valid_json(self, tmp_path):
        path = str(tmp_path / "test.json")
        result = export_json(SAMPLE_BOOKMARKS, path)
        data = json.loads(Path(result).read_text(encoding="utf-8"))
        assert data["count"] == 2
        assert len(data["bookmarks"]) == 2


class TestExportHTML:
    def test_export_creates_html(self, tmp_path):
        path = str(tmp_path / "test.html")
        result = export_html(SAMPLE_BOOKMARKS, path)
        content = Path(result).read_text(encoding="utf-8")
        assert "<html" in content
        assert "Python Tutorial" in content
        assert "searchInput" in content  # Has search functionality


class TestExportEPUB:
    def test_export_creates_epub(self, tmp_path):
        path = str(tmp_path / "test.epub")
        result = export_epub(SAMPLE_BOOKMARKS, path)
        assert Path(result).exists()
        # Verify it's a valid ZIP (EPUB is a ZIP)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "OEBPS/content.opf" in names


class TestExportBookmarks:
    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Unknown format"):
            export_bookmarks([], "xml")

    def test_default_output_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = export_bookmarks(SAMPLE_BOOKMARKS, "json")
        assert result.endswith(".json")
        assert Path(result).exists()
