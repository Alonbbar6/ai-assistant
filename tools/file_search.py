import os
import fnmatch
from pathlib import Path
from config import SEARCH_ROOTS, SEARCH_EXTENSIONS


def search_files(query: str, directory: str | None = None, extension: str | None = None) -> list[dict]:
    """
    Search for files by name pattern or content keyword.
    Returns list of {path, name, size_kb, modified} dicts.
    """
    roots = [directory] if directory else SEARCH_ROOTS
    results = []

    ext_filter = {extension.lower()} if extension else SEARCH_EXTENSIONS
    pattern = f"*{query}*" if query else "*"

    for root in roots:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip hidden dirs
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fname in filenames:
                _, ext = os.path.splitext(fname)
                if ext.lower() not in ext_filter:
                    continue
                if not fnmatch.fnmatch(fname.lower(), pattern.lower()):
                    continue
                full_path = Path(dirpath) / fname
                try:
                    stat = full_path.stat()
                    results.append({
                        "path": str(full_path),
                        "name": fname,
                        "size_kb": round(stat.st_size / 1024, 1),
                        "modified": _fmt_time(stat.st_mtime),
                    })
                except OSError:
                    pass
            if len(results) >= 50:
                break

    results.sort(key=lambda r: r["modified"], reverse=True)
    return results[:20]


def read_text_file(path: str) -> str:
    """Read and return the content of a text file (max 8 KB preview)."""
    path = Path(path)
    if not path.exists():
        return f"File not found: {path}"
    try:
        text = path.read_text(errors="replace")
        if len(text) > 8000:
            return text[:8000] + "\n\n[... truncated — file has more content ...]"
        return text
    except Exception as e:
        return f"Could not read file: {e}"


def _fmt_time(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
