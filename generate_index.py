import os
from datetime import datetime, timedelta

# Folder where your files are stored (root of repo)
FILES_DIR = "."

# Consider files new if modified within this many days
NEW_WINDOW = timedelta(days=2)


def is_new(file_path):
    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    return datetime.now() - mtime < NEW_WINDOW


def build_update_bar(files):
    new_links = []
    today = datetime.now().date()

    for f in files:
        if is_new(f):
            url = f.replace(" ", "%20")
            new_links.append(f'<a href="{url}" target="_blank">🆕 {os.path.basename(f)}</a>')

    if new_links:
        latest_file_time = max(os.path.getmtime(f) for f in files)
        latest_date = datetime.fromtimestamp(latest_file_time).date()
        label = "Uploaded today" if today == latest_date else f"Updated {today.strftime('%Y-%m-%d')}"
        return f'📢 {label} — ' + ", ".join(new_links)
    else:
        return f'📢 Updated {today.strftime("%Y-%m-%d")}'


def categorize_files():
    categories = {}
    all_files = []

    for f in os.listdir(FILES_DIR):
        if not os.path.isfile(f):
            continue
        if not (f.endswith(".pdf") or f.endswith(".epub")):
            continue

        all_files.append(f)

        # Detect course code (CS-501, CS-502, etc.)
        code = "Misc"
        for part in f.split("_"):
            if part.upper().startswith("CS-") or part.upper().startswith("CS"):
                code = part.upper().replace("CS", "CS-").replace("--", "-")
                break

        if code not in categories:
            categories[code] = []
        categories[code].append(f)

    return categories, all_files


def build_html(categories, update_bar):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSE • Notes & Assignments</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
  <style>
    body {{ background: #181e26; color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; min-height: 100vh; text-align: center; }}
    .lightmode {{ background: #f6f7f9; color: #232333; }}
    h1 {{ font-size:2.11rem;margin:30px 0 6px 0; }}
    .update-bar {{ background:#21396c; color:#e3ecfd; margin:20px auto 18px; padding:7px 22px; font-size:.99em; border-radius:13px; max-width:700px; }}
    section {{ margin:32px 0 16px 0; }}
    .section-title {{ margin-bottom:11px;font-size:1.11rem;text-transform:uppercase;letter-spacing:.7px; }}
    .file-list {{ list-style:none;padding:0;margin:13px 0; }}
    .file-list li {{ margin:9px 0; padding:9px 8px; background:#232b36; border-radius:9px; display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap; }}
    .download-link {{ display:inline-block; background:#203048;color:#8adcff;text-decoration:none;font-weight:500;font-size:1em; border-radius:8px;padding:6px 19px; }}
    .download-link:hover {{ background:#1e2a39;color:#b7f3ff; }}
    .file-size {{ font-size:.95em;color:#bbe1d7;margin-left:9px; }}
  </style>
</head>
<body>
  <h1>CSE Notes & Assignments</h1>
  <div class="update-bar">{update_bar}</div>
  <main>
"""

    for code, files in sorted(categories.items()):
        html += f"""    <section>
      <div class="section-title">{code}</div>
      <ul class="file-list">
"""
        for f in sorted(files):
            url = f.replace(" ", "%20")
            html += f"""        <li>
          <div>{os.path.basename(f)}</div>
          <div>
            <a href="{url}" target="_blank" class="download-link">Download</a>
            <span class="file-size"></span>
          </div>
        </li>
"""
        html += "      </ul>\n    </section>\n"

    html += """  </main>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    categories, all_files = categorize_files()
    update_bar = build_update_bar(all_files)
    html = build_html(categories, update_bar)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html updated with categorized sections and update bar")
            
