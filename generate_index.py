import os
import re
import datetime

# Path where your files (PDF, DOCX, etc.) are stored
ROOT = "."

# HTML header and footer (same style as you already have)
HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSE • Notes & Assignments</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    h1 { text-align: center; }
    .course-block { margin-bottom: 30px; }
    .file-list { list-style-type: none; padding: 0; }
    .file-list li { margin: 5px 0; }
    .new-banner { background: #ffeeba; padding: 10px; border: 1px solid #f0ad4e;
                  border-radius: 5px; margin-bottom: 20px; }
    .new-banner a { color: #c00; text-decoration: none; font-weight: bold; }
    .size { color: #555; font-size: 0.9em; margin-left: 5px; }
  </style>
</head>
<body>
<h1>📘 CSE Notes & Assignments</h1>
"""

HTML_FOOTER = """
</body>
</html>
"""

# Where to save the index file
OUTPUT_FILE = "index.html"

# Regex to extract course code (CS-501, CS-502, etc.)
COURSE_REGEX = re.compile(r"(CS-\d{3})", re.IGNORECASE)

# File extensions to include
ALLOWED_EXT = {".pdf", ".docx", ".epub", ".txt", ".md"}

# File storing timestamps of new uploads
META_FILE = ".file_timestamps"

def load_meta():
    """Load previous file timestamps to track 'new' files"""
    meta = {}
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            for line in f:
                fname, ts = line.strip().split("|")
                meta[fname] = float(ts)
    return meta

def save_meta(meta):
    """Save current file timestamps"""
    with open(META_FILE, "w") as f:
        for fname, ts in meta.items():
            f.write(f"{fname}|{ts}\n")

def file_size(path):
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"

def main():
    files = [f for f in os.listdir(ROOT) if os.path.isfile(f)]
    meta = load_meta()
    now = datetime.datetime.now().timestamp()
    new_files = []

    # Group files by course code
    courses = {}
    for f in sorted(files):
        ext = os.path.splitext(f)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        match = COURSE_REGEX.search(f)
        if match:
            course = match.group(1).upper()
        else:
            course = "Other"
        courses.setdefault(course, []).append(f)

        # Check if file is new (<3 days old)
        mtime = os.path.getmtime(f)
        if f not in meta or meta[f] < mtime:
            meta[f] = mtime
        if now - meta[f] <= 3 * 86400:
            new_files.append(f)

    save_meta(meta)

    # Build HTML
    html = [HTML_HEADER]

    # Banner for new files
    if new_files:
        banner = '<div class="new-banner">🆕 New files added: '
        links = []
        for f in new_files:
            links.append(f'<a href="{f}" download>{f}</a>')
        banner += " — ".join(links)
        banner += "</div>"
        html.append(banner)

    # Course sections
    for course, flist in sorted(courses.items()):
        html.append(f'<div class="course-block">')
        html.append(f"<h2>{course}</h2>")
        html.append('<ul class="file-list">')
        for f in sorted(flist):
            html.append(f'<li><a href="{f}" download>{f}</a>'
                        f'<span class="size">({file_size(f)})</span></li>')
        html.append("</ul></div>")

    html.append(HTML_FOOTER)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(html))


if __name__ == "__main__":
    main()
    
