"""
Export module for BookmarkHub.
Supports exporting bookmarks to Markdown, JSON, HTML, and EPUB formats.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _ensure_dir(path: Path) -> Path:
    """Ensure output directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def export_markdown(bookmarks: list[dict], output_path: str) -> str:
    """Export bookmarks to a Markdown file."""
    path = _ensure_dir(Path(output_path))
    lines = [
        "# 📚 BookmarkHub Export",
        f"\n_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        f"_Total bookmarks: {len(bookmarks)}_\n",
    ]
    # Group by source
    by_source: dict[str, list[dict]] = {}
    for bm in bookmarks:
        src = bm.get("source", "unknown")
        by_source.setdefault(src, []).append(bm)

    for source, items in sorted(by_source.items()):
        lines.append(f"\n## 🌐 {source.title()}\n")
        for bm in items:
            tags = json.loads(bm.get("tags", "[]")) if isinstance(bm.get("tags"), str) else bm.get("tags", [])
            tag_str = " ".join(f"`{t}`" for t in tags) if tags else ""
            lines.append(f"- [{bm.get('title', bm.get('url'))}]({bm.get('url')})  ")
            if bm.get("description"):
                lines.append(f"  _{bm['description']}_")
            if tag_str:
                lines.append(f"  {tag_str}")
            lines.append(f"  📅 {bm.get('created_at', '')[:10]}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def export_json(bookmarks: list[dict], output_path: str) -> str:
    """Export bookmarks to a JSON file."""
    path = _ensure_dir(Path(output_path))
    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(bookmarks),
        "bookmarks": bookmarks,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def export_html(bookmarks: list[dict], output_path: str) -> str:
    """Export bookmarks to a standalone HTML file with built-in search."""
    path = _ensure_dir(Path(output_path))
    # Group by source
    by_source: dict[str, list[dict]] = {}
    for bm in bookmarks:
        src = bm.get("source", "unknown")
        by_source.setdefault(src, []).append(bm)

    source_tabs = "\n".join(
        f'<button class="tab-btn" data-source="{src}">{src.title()} ({len(items)})</button>'
        for src, items in sorted(by_source.items())
    )
    bookmark_items = []
    for source, items in sorted(by_source.items()):
        for bm in items:
            tags = json.loads(bm.get("tags", "[]")) if isinstance(bm.get("tags"), str) else bm.get("tags", [])
            tag_html = " ".join(f'<span class="tag">{t}</span>' for t in tags)
            bookmark_items.append(
                f'<div class="bookmark" data-source="{source}">'
                f'<h3><a href="{bm.get("url")}" target="_blank">{bm.get("title", bm.get("url"))}</a></h3>'
                f'<p class="desc">{bm.get("description", "")}</p>'
                f'<div class="meta">{tag_html} <span class="date">📅 {bm.get("created_at", "")[:10]}</span></div>'
                f'</div>'
            )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📚 BookmarkHub Export</title>
<style>
  :root {{ --bg: #1a1b26; --surface: #24283b; --text: #c0caf5; --accent: #7aa2f7; --tag: #bb9af7; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 2rem; }}
  h1 {{ color: var(--accent); margin-bottom: 1rem; }}
  .search {{ width: 100%; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid var(--surface); background: var(--surface); color: var(--text); font-size: 1rem; margin-bottom: 1rem; }}
  .tabs {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
  .tab-btn {{ padding: 0.5rem 1rem; border-radius: 6px; border: 1px solid var(--surface); background: var(--surface); color: var(--text); cursor: pointer; }}
  .tab-btn.active {{ background: var(--accent); color: var(--bg); }}
  .bookmark {{ background: var(--surface); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }}
  .bookmark h3 a {{ color: var(--accent); text-decoration: none; }}
  .bookmark h3 a:hover {{ text-decoration: underline; }}
  .desc {{ color: #a9b1d6; font-size: 0.9rem; margin: 0.25rem 0; }}
  .tag {{ background: rgba(187,154,247,0.15); color: var(--tag); padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px; }}
  .date {{ color: #565f89; font-size: 0.8rem; }}
  .meta {{ margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
</style>
</head>
<body>
<h1>📚 BookmarkHub Export</h1>
<p>{len(bookmarks)} bookmarks · Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</p>
<input class="search" type="text" placeholder="🔍 Search bookmarks..." id="searchInput">
<div class="tabs">
  <button class="tab-btn active" data-source="all">All ({len(bookmarks)})</button>
  {source_tabs}
</div>
<div id="bookmarks">{''.join(bookmark_items)}</div>
<script>
const searchInput = document.getElementById('searchInput');
const tabs = document.querySelectorAll('.tab-btn');
let activeSource = 'all';
searchInput.addEventListener('input', e => {{
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.bookmark').forEach(b => {{
    const text = b.textContent.toLowerCase();
    const matchSource = activeSource === 'all' || b.dataset.source === activeSource;
    b.style.display = matchSource && text.includes(q) ? '' : 'none';
  }});
}});
tabs.forEach(tab => tab.addEventListener('click', () => {{
  tabs.forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  activeSource = tab.dataset.source;
  searchInput.dispatchEvent(new Event('input'));
}}));
</script>
</body>
</html>"""
    path.write_text(html, encoding="utf-8")
    return str(path)


def export_epub(bookmarks: list[dict], output_path: str) -> str:
    """Export bookmarks to EPUB format (lightweight, no external deps)."""
    path = _ensure_dir(Path(output_path))
    # Minimal valid EPUB structure
    import zipfile
    import uuid

    epub_uuid = str(uuid.uuid4())
    by_source: dict[str, list[dict]] = {}
    for bm in bookmarks:
        src = bm.get("source", "unknown")
        by_source.setdefault(src, []).append(bm)

    # Build chapter content
    chapters = []
    for source, items in sorted(by_source.items()):
        items_html = ""
        for bm in items:
            tags = json.loads(bm.get("tags", "[]")) if isinstance(bm.get("tags"), str) else bm.get("tags", [])
            tag_str = ", ".join(tags)
            items_html += f"""<div style="margin-bottom:1em;">
<h3><a href="{bm.get('url')}">{bm.get('title', bm.get('url'))}</a></h3>
<p>{bm.get('description', '')}</p>
<p><small>Tags: {tag_str} | {bm.get('created_at', '')[:10]}</small></p>
</div>\n"""
        chapters.append((source, items_html))

    # mimetype must be first and stored (no compression)
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # META-INF/container.xml
        zf.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")

        # content.opf
        manifest_items = ""
        spine_items = ""
        for i, (source, _) in enumerate(chapters):
            fid = f"ch{i}"
            manifest_items += f'<item id="{fid}" href="{fid}.xhtml" media-type="application/xhtml+xml"/>\n'
            spine_items += f'<itemref idref="{fid}"/>\n'
        zf.writestr("OEBPS/content.opf", f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:{epub_uuid}</dc:identifier>
    <dc:title>BookmarkHub Export</dc:title>
    <dc:creator>BookmarkHub</dc:creator>
    <dc:date>{datetime.now(timezone.utc).strftime('%Y-%m-%d')}</dc:date>
    <meta property="dcterms:modified">{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    {manifest_items}
  </manifest>
  <spine>
    <itemref idref="nav"/>
    {spine_items}
  </spine>
</package>""")

        # nav.xhtml
        nav_items = "\n".join(
            f'<li><a href="ch{i}.xhtml">{src.title()}</a></li>'
            for i, (src, _) in enumerate(chapters)
        )
        zf.writestr("OEBPS/nav.xhtml", f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>BookmarkHub</title></head>
<body>
<nav epub:type="toc"><h1>Table of Contents</h1><ol>{nav_items}</ol></nav>
</body></html>""")

        # Chapter files
        for i, (source, html) in enumerate(chapters):
            zf.writestr(f"OEBPS/ch{i}.xhtml", f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{source.title()}</title></head>
<body><h1>🌐 {source.title()}</h1>{html}</body></html>""")

    return str(path)


EXPORTERS = {
    "markdown": export_markdown,
    "json": export_json,
    "html": export_html,
    "epub": export_epub,
}


def export_bookmarks(
    bookmarks: list[dict], fmt: str, output_path: Optional[str] = None
) -> str:
    """Export bookmarks in the specified format."""
    if fmt not in EXPORTERS:
        raise ValueError(f"Unknown format: {fmt}. Available: {', '.join(EXPORTERS.keys())}")
    if not output_path:
        ext = {"markdown": "md", "json": "json", "html": "html", "epub": "epub"}[fmt]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"exports/bookmarkhub_{timestamp}.{ext}"
    return EXPORTERS[fmt](bookmarks, output_path)

