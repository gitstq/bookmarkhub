"""
BookmarkHub CLI - Main entry point.
Multi-platform bookmark collector, searcher, organizer & exporter.
"""

import json
import sys
import os

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .db import BookmarkDB
from .fetchers import FETCHERS, get_fetcher
from .exporter import export_bookmarks

console = Console()


def _parse_tags(tags_str: str) -> list[str]:
    """Parse comma-separated tags string into a list."""
    return [t.strip() for t in tags_str.split(",") if t.strip()]


@click.group()
@click.version_option(version=__version__, prog_name="bookmarkhub")
def main():
    """🌐 BookmarkHub - Multi-platform bookmark collector, searcher & exporter CLI"""
    pass


# ──────────────────────────── Sync Commands ────────────────────────────

@main.command()
@click.argument("platform", type=click.Choice(list(FETCHERS.keys())))
@click.option("--limit", "-l", default=30, help="Max items to fetch")
@click.option("--subreddit", "-s", default="popular", help="Subreddit (Reddit only)")
@click.option("--language", "-L", default="", help="Language filter (GitHub only)")
@click.option("--since", default="daily", type=click.Choice(["daily", "weekly", "monthly"]), help="Time range (GitHub only)")
def sync(platform: str, limit: int, subreddit: str, language: str, since: str):
    """🔄 Fetch and sync bookmarks from a platform."""
    db = BookmarkDB()
    fetcher = get_fetcher(platform)
    try:
        with console.status(f"[bold green]Fetching from {platform}..."):
            kwargs = {"limit": limit}
            if platform == "reddit":
                kwargs["subreddit"] = subreddit
            elif platform == "github":
                kwargs["language"] = language
                kwargs["since"] = since
            bookmarks = fetcher.fetch(**kwargs)
        if not bookmarks:
            console.print(f"[yellow]No bookmarks found from {platform}.[/yellow]")
            return
        added = db.add_bookmarks_batch(bookmarks)
        console.print(f"[bold green]✅ Synced {len(bookmarks)} bookmarks from {platform} ({added} new)[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        sys.exit(1)
    finally:
        db.close()


@main.command(name="sync-all")
@click.option("--limit", "-l", default=30, help="Max items per platform")
def sync_all(limit: int):
    """🔄 Fetch and sync from ALL supported platforms."""
    db = BookmarkDB()
    total_added = 0
    for name in FETCHERS:
        try:
            with console.status(f"[bold green]Fetching from {name}..."):
                fetcher = get_fetcher(name)
                bookmarks = fetcher.fetch(limit=limit)
            if bookmarks:
                added = db.add_bookmarks_batch(bookmarks)
                total_added += added
                console.print(f"  [green]✅ {name}: {len(bookmarks)} fetched, {added} new[/green]")
            else:
                console.print(f"  [yellow]⚠️ {name}: No bookmarks found[/yellow]")
        except Exception as e:
            console.print(f"  [red]❌ {name}: {e}[/red]")
    console.print(f"\n[bold green]🎉 Total new bookmarks added: {total_added}[/bold green]")
    db.close()


# ──────────────────────────── Add Command ────────────────────────────

@main.command()
@click.argument("url")
@click.option("--title", "-t", default="", help="Bookmark title")
@click.option("--description", "-d", default="", help="Bookmark description")
@click.option("--tags", "-T", default="", help="Comma-separated tags")
def add(url: str, title: str, description: str, tags: str):
    """➕ Add a bookmark manually."""
    db = BookmarkDB()
    try:
        tag_list = _parse_tags(tags) if tags else None
        bid = db.add_bookmark(url=url, title=title, description=description, source="manual", tags=tag_list)
        if bid > 0:
            console.print(f"[bold green]✅ Bookmark added (ID: {bid})[/bold green]")
        else:
            console.print("[yellow]⚠️ Bookmark already exists.[/yellow]")
    finally:
        db.close()


# ──────────────────────────── Search Command ────────────────────────────

@main.command()
@click.argument("query")
@click.option("--source", "-s", default=None, help="Filter by source platform")
@click.option("--limit", "-l", default=20, help="Max results")
def search(query: str, source: str, limit: int):
    """🔍 Full-text search across all bookmarks."""
    db = BookmarkDB()
    try:
        results = db.search(query, limit=limit, source=source)
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
        table = Table(title=f"🔍 Search: '{query}'", show_lines=True)
        table.add_column("ID", style="dim", width=5)
        table.add_column("Title", style="bold cyan", max_width=40)
        table.add_column("Source", style="magenta", width=12)
        table.add_column("Tags", style="green", max_width=25)
        table.add_column("Date", style="dim", width=10)
        for r in results:
            tags = json.loads(r["tags"]) if isinstance(r["tags"], str) else r["tags"]
            table.add_row(
                str(r["id"]),
                r["title"][:40] or r["url"][:40],
                r["source"],
                ", ".join(tags),
                r["created_at"][:10],
            )
        console.print(table)
    finally:
        db.close()


# ──────────────────────────── List Command ────────────────────────────

@main.command(name="list")
@click.option("--source", "-s", default=None, help="Filter by source")
@click.option("--tag", "-t", default=None, help="Filter by tag")
@click.option("--limit", "-l", default=20, help="Max results")
@click.option("--offset", "-o", default=0, help="Offset for pagination")
def list_cmd(source: str, tag: str, limit: int, offset: int):
    """📋 List bookmarks with optional filtering."""
    db = BookmarkDB()
    try:
        bookmarks = db.list_bookmarks(source=source, tag=tag, limit=limit, offset=offset)
        if not bookmarks:
            console.print("[yellow]No bookmarks found.[/yellow]")
            return
        table = Table(title="📚 Bookmarks", show_lines=True)
        table.add_column("ID", style="dim", width=5)
        table.add_column("Title", style="bold cyan", max_width=40)
        table.add_column("Source", style="magenta", width=12)
        table.add_column("Tags", style="green", max_width=25)
        table.add_column("Date", style="dim", width=10)
        for bm in bookmarks:
            tags = json.loads(bm["tags"]) if isinstance(bm["tags"], str) else bm["tags"]
            table.add_row(
                str(bm["id"]),
                bm["title"][:40] or bm["url"][:40],
                bm["source"],
                ", ".join(tags),
                bm["created_at"][:10],
            )
        console.print(table)
    finally:
        db.close()


# ──────────────────────────── Stats Command ────────────────────────────

@main.command()
def stats():
    """📊 Show bookmark statistics."""
    db = BookmarkDB()
    try:
        s = db.get_stats()
        console.print(f"\n[bold]📚 BookmarkHub Statistics[/bold]\n")
        console.print(f"  Total bookmarks: [bold cyan]{s['total']}[/bold cyan]")
        console.print("\n  [bold]By Source:[/bold]")
        for src, cnt in s["by_source"].items():
            bar = "█" * min(cnt, 30)
            console.print(f"    {src:15s} {bar} {cnt}")
        if s["top_tags"]:
            console.print("\n  [bold]Top Tags:[/bold]")
            for tag, cnt in s["top_tags"]:
                console.print(f"    {tag:15s} {cnt}")
    finally:
        db.close()


# ──────────────────────────── Export Command ────────────────────────────

@main.command()
@click.argument("format", type=click.Choice(["markdown", "json", "html", "epub"]))
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--source", "-s", default=None, help="Filter by source")
@click.option("--tag", "-t", default=None, help="Filter by tag")
def export(format: str, output: str, source: str, tag: str):
    """📤 Export bookmarks to various formats."""
    db = BookmarkDB()
    try:
        bookmarks = db.list_bookmarks(source=source, tag=tag, limit=99999, offset=0)
        if not bookmarks:
            console.print("[yellow]No bookmarks to export.[/yellow]")
            return
        path = export_bookmarks(bookmarks, format, output)
        console.print(f"[bold green]✅ Exported {len(bookmarks)} bookmarks to {path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Export failed: {e}[/bold red]")
        sys.exit(1)
    finally:
        db.close()


# ──────────────────────────── Delete Command ────────────────────────────

@main.command()
@click.argument("bookmark_id", type=int)
def delete(bookmark_id: int):
    """🗑️ Delete a bookmark by ID."""
    db = BookmarkDB()
    try:
        if db.delete_bookmark(bookmark_id):
            console.print(f"[bold green]✅ Bookmark {bookmark_id} deleted.[/bold green]")
        else:
            console.print(f"[yellow]⚠️ Bookmark {bookmark_id} not found.[/yellow]")
    finally:
        db.close()


if __name__ == "__main__":
    main()
