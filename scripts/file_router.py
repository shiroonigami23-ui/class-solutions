#!/usr/bin/env python3
import argparse
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "content"

SKIP_FILES = {
    "index.html",
    "style.css",
    "script.js",
    "profile.js",
    "preview.js",
    "manifest.json",
    "sw.js",
    "README.md",
    "LICENSE",
    "contribute.html",
    "contribution_handler.js",
    "contributors.json",
    "subjects.yaml",
    "generate_index.py",
    "update_contributors.py",
}

SKIP_PREFIXES = (".",)
SKIP_DIRS = {".git", ".github", "node_modules", "scripts", "content"}
ASSET_FILES = {
    "app.png",
    "image.png",
    "pdf.png",
    "notes.png",
    "jpg.png",
    "jpeg.png",
    "txt.png",
    "bg.mp4",
    "profile-bg.mp4",
    "shiro.png",
}

SEMESTER_MAP = {
    "CS-501": "sem5",
    "CS-502": "sem5",
    "CS-503": "sem5",
    "CS-504": "sem5",
    "CS-601": "sem6",
    "CS-602": "sem6",
    "CS-603": "sem6",
    "CS-604": "sem6",
}

EXT_TO_BUCKET = {
    ".pdf": "documents",
    ".epub": "notes",
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".md": "text",
    ".txt": "text",
}


def slugify(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "file"


def detect_course(name: str) -> str:
    name_u = name.upper()
    m = re.search(r"(CS)\s*[-_ ]?(\d{3})", name_u)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    if "DBMS" in name_u or "RDBMS" in name_u:
        return "CS-502"
    if "CYBER" in name_u or "DATA_ANALYTICS" in name_u or "DATA ANALYTICS" in name_u:
        return "CS-503"
    if "WEB" in name_u or "IAWT" in name_u:
        return "CS-504"
    if "TOC" in name_u or "AUTOMATA" in name_u:
        return "CS-501"
    return "GENERAL"


def detect_kind(name: str) -> str:
    n = name.lower()
    if "assignment" in n:
        return "assignment"
    if "solution" in n:
        return "solution"
    if "notes" in n or "note" in n:
        return "notes"
    if "lab" in n:
        return "lab"
    if "project" in n:
        return "project"
    if "question" in n or "paper" in n:
        return "question-bank"
    return "resource"


def target_bucket(ext: str, kind: str) -> str:
    if kind == "assignment":
        return "assignments"
    if kind == "solution":
        return "solutions"
    if kind in {"notes", "lab", "question-bank"} and ext in {".pdf", ".epub", ".txt", ".md"}:
        return "notes"
    return EXT_TO_BUCKET.get(ext, "misc")


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    i = 2
    while True:
        candidate = path.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def route_file(file_path: Path) -> Path:
    ext = file_path.suffix.lower()
    course = detect_course(file_path.name)
    semester = SEMESTER_MAP.get(course, "general")
    kind = detect_kind(file_path.name)
    bucket = target_bucket(ext, kind)
    slug = slugify(file_path.stem)

    target_dir = CONTENT_ROOT / semester / course.lower() / bucket
    target_dir.mkdir(parents=True, exist_ok=True)

    new_name = f"{semester}_{course.lower()}_{kind}_{slug}{ext}"
    target_path = unique_path(target_dir / new_name)
    shutil.move(str(file_path), str(target_path))
    return target_path.relative_to(ROOT)


def iter_root_files():
    for item in ROOT.iterdir():
        if item.is_dir():
            continue
        if item.name in SKIP_FILES or item.name in ASSET_FILES:
            continue
        if any(item.name.startswith(prefix) for prefix in SKIP_PREFIXES):
            continue
        yield item


def main():
    parser = argparse.ArgumentParser(description="Route uploaded files into organized folders.")
    parser.add_argument("--file", help="Single file path (relative to repo root).")
    parser.add_argument("--bulk", action="store_true", help="Route all eligible files from repository root.")
    args = parser.parse_args()

    if args.file:
        src = (ROOT / args.file).resolve()
        if not src.exists():
            raise SystemExit(f"File not found: {args.file}")
        routed = route_file(src)
        print(routed.as_posix())
        return

    if args.bulk:
        moved = []
        for file_path in iter_root_files():
            moved.append(route_file(file_path).as_posix())
        print(f"ROUTED_COUNT={len(moved)}")
        for p in moved:
            print(p)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
