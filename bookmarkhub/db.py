"""
Database layer for BookmarkHub.
Uses SQLite with FTS5 for full-text search.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = Path.home() / ".bookmarkhub" / "bookmarks.db"

# Auto-tag rules: keyword -> tag
AUTO_TAG_RULES = {
    "python": "programming",
    "javascript": "programming",
    "typescript": "programming",
    "rust": "programming",
    "golang": "programming",
    "go ": "programming",
    "react": "frontend",
    "vue": "frontend",
    "css": "frontend",
    "html": "frontend",
    "ai": "ai",
    "llm": "ai",
    "gpt": "ai",
    "claude": "ai",
    "machine learning": "ai",
    "deep learning": "ai",
    "security": "security",
    "hacking": "security",
    "vulnerability": "security",
    "cve": "security",
    "docker": "devops",
    "kubernetes": "devops",
    "k8s": "devops",
    "ci/cd": "devops",
    "database": "data",
    "sql": "data",
    "postgres": "data",
    "mongodb": "data",
    "design": "design",
    "ui": "design",
    "ux": "design",
}


def _auto_tag(title: str, description: str) -> list[str]:
    """Generate automatic tags based on content keywords."""
    text = f"{title} {description}".lower()
    tags = set()
    for keyword, tag in AUTO_TAG_RULES.items():
        if keyword in text:
            tags.add(tag)
    return sorted(tags)


class BookmarkDB:
    """SQLite database manager for bookmarks with FTS5 full-text search."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize database schema with FTS5 virtual table."""
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT 'manual',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                UNIQUE(url, source)
            )
        """)
        # FTS5 virtual table for full-text search
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bookmarks_fts USING fts5(
                title, description, url, tags,
                content=bookmarks,
                content_rowid=id
            )
        """)
        # Triggers to keep FTS in sync
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS bookmarks_ai AFTER INSERT ON bookmarks BEGIN
                INSERT INTO bookmarks_fts(rowid, title, description, url, tags)
                VALUES (new.id, new.title, new.description, new.url, new.tags);
            END
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS bookmarks_ad AFTER DELETE ON bookmarks BEGIN
                INSERT INTO bookmarks_fts(bookmarks_fts, rowid, title, description, url, tags)
                VALUES ('delete', old.id, old.title, old.description, old.url, old.tags);
            END
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS bookmarks_au AFTER UPDATE ON bookmarks BEGIN
                INSERT INTO bookmarks_fts(bookmarks_fts, rowid, title, description, url, tags)
                VALUES ('delete', old.id, old.title, old.description, old.url, old.tags);
                INSERT INTO bookmarks_fts(rowid, title, description, url, tags)
                VALUES (new.id, new.title, new.description, new.url, new.tags);
            END
        """)
        self.conn.commit()

    def add_bookmark(
        self,
        url: str,
        title: str = "",
        description: str = "",
        source: str = "manual",
        tags: Optional[list[str]] = None,
    ) -> int:
        """Add a single bookmark. Returns the bookmark ID."""
        now = datetime.now(timezone.utc).isoformat()
        auto_tags = _auto_tag(title, description)
        if tags:
            all_tags = sorted(set(tags + auto_tags))
        else:
            all_tags = auto_tags
        tags_json = json.dumps(all_tags)
        try:
            cur = self.conn.execute(
                """INSERT INTO bookmarks (url, title, description, source, tags, created_at, synced_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(url, source) DO UPDATE SET
                       title=excluded.title,
                       description=excluded.description,
                       tags=excluded.tags,
                       synced_at=excluded.synced_at
                """,
                (url, title, description, source, tags_json, now, now),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return -1

    def add_bookmarks_batch(self, bookmarks: list[dict]) -> int:
        """Add multiple bookmarks at once. Returns count of newly added."""
        added = 0
        for bm in bookmarks:
            bid = self.add_bookmark(
                url=bm["url"],
                title=bm.get("title", ""),
                description=bm.get("description", ""),
                source=bm.get("source", "manual"),
                tags=bm.get("tags"),
            )
            if bid > 0:
                added += 1
        return added

    def search(self, query: str, limit: int = 50, source: Optional[str] = None) -> list[dict]:
        """Full-text search across bookmarks."""
        sql = """
            SELECT b.* FROM bookmarks b
            JOIN bookmarks_fts f ON b.id = f.rowid
            WHERE bookmarks_fts MATCH ?
        """
        params: list = [query]
        if source:
            sql += " AND b.source = ?"
            params.append(source)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def list_bookmarks(
        self,
        source: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List bookmarks with optional filtering."""
        sql = "SELECT * FROM bookmarks WHERE 1=1"
        params: list = []
        if source:
            sql += " AND source = ?"
            params.append(source)
        if tag:
            sql += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        """Get bookmark statistics."""
        cur = self.conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]
        sources = cur.execute(
            "SELECT source, COUNT(*) as cnt FROM bookmarks GROUP BY source ORDER BY cnt DESC"
        ).fetchall()
        tags_raw = cur.execute("SELECT tags FROM bookmarks").fetchall()
        tag_counts: dict[str, int] = {}
        for row in tags_raw:
            for t in json.loads(row[0]):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:10]
        return {
            "total": total,
            "by_source": {r[0]: r[1] for r in sources},
            "top_tags": top_tags,
        }

    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark by ID."""
        cur = self.conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def close(self):
        """Close database connection."""
        self.conn.close()
