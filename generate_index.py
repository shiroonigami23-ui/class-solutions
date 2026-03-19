import datetime
import html
import json
import os
import re
import subprocess
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    yaml = None

SUPPORTED_EXTENSIONS = [".pdf", ".epub", ".jpg", ".png", ".jpeg", ".txt", ".md"]
IGNORE_FILES = {
    "README.md",
    "generate_index.py",
    "style.css",
    "script.js",
    "profile.js",
    "preview.js",
    "index.html",
    "contribute.html",
    "contribution_handler.js",
    "contributors.json",
    "update_contributors.py",
    "subjects.yaml",
}
IGNORE_DIRS = {".git", ".github", "scripts", "node_modules"}
ROOT_ASSET_FILES = {
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

FILE_TYPE_MAP = {
    ".pdf": {"category": "Documents", "icon": "pdf.png"},
    ".epub": {"category": "Notes", "icon": "notes.png"},
    ".jpg": {"category": "Images", "icon": "jpg.png"},
    ".jpeg": {"category": "Images", "icon": "jpeg.png"},
    ".png": {"category": "Images", "icon": "image.png"},
    ".txt": {"category": "Text Files", "icon": "txt.png"},
    ".md": {"category": "Text Files", "icon": "txt.png"},
}

DEFAULT_COURSES = {
    "CS-501": {"semester": "5", "keywords": ["toc", "automata", "nfa", "dfa", "cs501"]},
    "CS-502": {"semester": "5", "keywords": ["dbms", "rdbms", "database", "cs502"]},
    "CS-503": {"semester": "5", "keywords": ["cyber", "security", "data analytics", "cs503"]},
    "CS-504": {"semester": "5", "keywords": ["internet", "web", "iwd", "cs504"]},
    "CS-601": {"semester": "6", "keywords": ["cs601", "machine learning", "ml"]},
    "CS-602": {"semester": "6", "keywords": ["cs602", "computer network", "network"]},
    "CS-603": {"semester": "6", "keywords": ["cs603", "compiler", "graphics"]},
    "CS-604": {"semester": "6", "keywords": ["cs604", "project management", "pm"]},
    "CS-605": {"semester": "6", "keywords": ["cs605", "data analytics lab", "dal"]},
    "CS-606": {"semester": "6", "keywords": ["cs606", "skill development", "hnd"]},
}

DEFAULT_SEMESTERS = {
    "5": "Semester 5",
    "6": "Semester 6",
}


def load_contributors() -> Dict[str, str]:
    try:
        with open("contributors.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}


def load_subject_config(config_path: str = "subjects.yaml") -> Dict:
    config = {
        "courses": dict(DEFAULT_COURSES),
        "semesters": dict(DEFAULT_SEMESTERS),
        "file_overrides": {},
    }

    if not os.path.exists(config_path):
        return config

    if yaml is None:
        print("WARNING: PyYAML is not installed. Using default course/semester mapping.")
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file) or {}
    except Exception as error:
        print(f"WARNING: Could not parse {config_path}: {error}. Using defaults.")
        return config

    loaded_courses = loaded.get("courses", {})
    if isinstance(loaded_courses, dict):
        for code, meta in loaded_courses.items():
            if not isinstance(meta, dict):
                continue
            merged = dict(config["courses"].get(code, {}))
            merged.update(meta)
            merged["keywords"] = [str(k).lower() for k in merged.get("keywords", [])]
            merged["semester"] = str(merged.get("semester", "General"))
            config["courses"][code] = merged

    loaded_semesters = loaded.get("semesters", {})
    if isinstance(loaded_semesters, dict):
        for sem_key, sem_name in loaded_semesters.items():
            config["semesters"][str(sem_key)] = str(sem_name)

    loaded_overrides = loaded.get("file_overrides", {})
    if isinstance(loaded_overrides, dict):
        config["file_overrides"] = {str(name).lower(): meta for name, meta in loaded_overrides.items() if isinstance(meta, dict)}

    return config


def get_file_creation_date(filepath: str) -> datetime.datetime:
    try:
        ts_output = subprocess.check_output(["git", "log", "--diff-filter=A", "--format=%at", "--", filepath]).decode().strip()
        if ts_output:
            return datetime.datetime.fromtimestamp(int(ts_output.split("\n")[-1]))
    except Exception:
        pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))


def get_file_size(filepath: str) -> str:
    size = os.path.getsize(filepath)
    if size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 ** 2):.2f} MB"


def format_title(filename: str) -> str:
    stem = os.path.splitext(os.path.basename(filename))[0]
    routed = re.match(r"^(sem\d+|general)_(cs-\d+|general)_[a-z-]+_(.+)$", stem, re.IGNORECASE)
    if routed:
        stem = routed.group(3)
    title = stem.replace("_", " ").replace("-", " ")
    title = re.sub(r"^(cs\s*\d+\s*)", "", title, flags=re.IGNORECASE).strip()
    return title.title()


def _normalize_for_match(text: str) -> str:
    """Normalize filename for keyword matching: lowercase, no hyphens/spaces/underscores."""
    return re.sub(r"[\s\-_]+", "", text.lower())


def resolve_course(filename: str, courses: Dict[str, Dict], file_override: Dict) -> str:
    if file_override.get("course"):
        return str(file_override["course"])

    normalized = filename.lower()
    normalized_compact = _normalize_for_match(filename)
    best_course = "Uncategorized"
    best_score = 0

    for code, meta in courses.items():
        keywords = [str(word).lower() for word in meta.get("keywords", [])]
        score = 0
        for word in keywords:
            if not word:
                continue
            word_compact = _normalize_for_match(word)
            if word in normalized or word_compact in normalized_compact:
                score += 1
        if score > best_score:
            best_course = code
            best_score = score

    return best_course


def resolve_semester(filename: str, course: str, courses: Dict[str, Dict], file_override: Dict) -> str:
    if file_override.get("semester"):
        return str(file_override["semester"])

    if course in courses and courses[course].get("semester"):
        return str(courses[course]["semester"])

    sem_match = re.search(r"sem(?:ester)?\s*[-_ ]?(\d+)", filename, re.IGNORECASE)
    if sem_match:
        return sem_match.group(1)

    return "General"


def extract_keywords(file_info: Dict, file_override: Dict) -> str:
    keywords = set()

    override_keywords = file_override.get("keywords", [])
    if isinstance(override_keywords, list):
        keywords.update(str(item).lower() for item in override_keywords)

    meta_filepath = os.path.splitext(file_info["name"])[0] + ".meta"
    if os.path.exists(meta_filepath):
        with open(meta_filepath, "r", encoding="utf-8") as file:
            keywords.update(file.read().lower().split())

    if file_info["ext"] in [".txt", ".md"]:
        try:
            with open(file_info["name"], "r", encoding="utf-8") as file:
                content = file.read(500).lower()
                words = re.findall(r"\b\w+\b", content)
                keywords.update(words)
        except Exception as error:
            print(f"WARNING: Could not read {file_info['name']} for keywords: {error}")

    return " ".join(sorted(keywords))


def generate_file_html(file_info: Dict, contributors: Dict[str, str], file_override: Dict) -> str:
    title = file_override.get("title") or format_title(file_info["name"])
    contributor_name = contributors.get(file_info["name"]) or contributors.get(file_info.get("path", ""))

    base_keywords = f"{title} {file_info['course']} semester {file_info['semester']}"
    content_keywords = extract_keywords(file_info, file_override)
    all_keywords = f"{base_keywords} {content_keywords}".strip()

    contributor_html = ""
    if contributor_name:
        contributor_html = (
            f'<div class="contributor-credit">Added by '
            f'<a href="https://github.com/{html.escape(contributor_name)}" target="_blank">'
            f'@{html.escape(contributor_name)}</a></div>'
        )

    preview_button_html = ""
    if file_info["ext"] == ".pdf":
        preview_button_html = f'<button class="preview-button" data-pdf-url="{html.escape(file_info.get("path", file_info["name"]))}">Preview</button>'

    file_name = html.escape(file_info.get("path", file_info["name"]))
    safe_title = html.escape(title)
    safe_keywords = html.escape(all_keywords)
    safe_course = html.escape(file_info["course"])
    safe_semester = html.escape(str(file_info["semester"]))
    safe_size = html.escape(file_info["size"])
    icon = html.escape(FILE_TYPE_MAP.get(file_info["ext"], {}).get("icon", "txt.png"))
    ext = html.escape(file_info["ext"])

    return f"""
    <div class="file-card file-row" data-keywords="{safe_keywords}" data-course="{safe_course}" data-semester="{safe_semester}" data-type="{html.escape(file_info['ext'].lstrip('.'))}" data-date="{html.escape(file_info['date'].isoformat())}">
        <div class="file-icon"><img src="{icon}" alt="{ext} icon"></div>
        <div class="file-details">
            <div class="file-title">{safe_title}</div>
            <div class="file-meta"><span>{safe_course}</span><span>Sem {safe_semester}</span><span>{safe_size}</span></div>
            {contributor_html}
        </div>
        <div class="file-actions">
            {preview_button_html}
            <a href="{file_name}" target="_blank" class="download-button" aria-label="Open {safe_title}">View</a>
        </div>
    </div>"""


def sort_semesters(semester_values: List[str]) -> List[str]:
    def sort_key(value: str) -> Tuple[int, str]:
        if str(value).isdigit():
            return (0, str(int(value)))
        return (1, str(value))

    unique = sorted(set(str(item) for item in semester_values), key=sort_key)
    return unique


def main() -> None:
    config = load_subject_config()
    contributors = load_contributors()

    courses = config["courses"]
    semesters = config["semesters"]
    file_overrides = config["file_overrides"]

    all_files = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in files:
            rel_path = os.path.relpath(os.path.join(root, filename), ".").replace("\\", "/")
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            if filename in IGNORE_FILES or filename.startswith("."):
                continue
            if root == "." and filename in ROOT_ASSET_FILES:
                continue

            override = file_overrides.get(filename.lower(), {}) or file_overrides.get(rel_path.lower(), {})
            path_tokens = rel_path.split("/")
            path_course = None
            path_semester = None
            for token in path_tokens:
                if re.fullmatch(r"cs-\d{3}", token.lower()):
                    path_course = token.upper()
                if re.fullmatch(r"sem\d+", token.lower()):
                    path_semester = token[3:]

            course = path_course or resolve_course(filename, courses, override)
            semester = str(path_semester) if path_semester else resolve_semester(filename, course, courses, override)
            if semester.lower() == "general":
                semester = "General"

            all_files.append(
                {
                    "name": filename,
                    "path": rel_path,
                    "ext": ext,
                    "size": get_file_size(rel_path),
                    "date": get_file_creation_date(rel_path),
                    "course": course,
                    "semester": semester,
                    "override": override,
                }
            )

    all_files.sort(key=lambda item: item["date"], reverse=True)

    categories = sorted({meta["category"] for meta in FILE_TYPE_MAP.values()})
    content_by_category = {"All Files": ""}
    for category in categories:
        content_by_category[category] = ""

    for file_info in all_files:
        card_html = generate_file_html(file_info, contributors, file_info["override"])
        content_by_category["All Files"] += card_html

        category = FILE_TYPE_MAP.get(file_info["ext"], {}).get("category")
        if category in content_by_category:
            content_by_category[category] += card_html

    tabs_html = ""
    panels_html = ""
    ordered_categories = ["All Files"] + [category for category in categories if content_by_category.get(category)]

    for index, category in enumerate(ordered_categories):
        content = content_by_category.get(category, "")
        if not content:
            continue
        tab_id = category.replace(" ", "")
        active_class = " active" if index == 0 else ""
        tabs_html += f'<button class="tab-link{active_class}" data-tab="{tab_id}">{html.escape(category)}</button>'
        panels_html += f'<div id="{tab_id}" class="tab-content" style="display: {"block" if index == 0 else "none"};"><div class="file-grid">{content}</div></div>'

    # Show all semesters from YAML first, then any from files (e.g. General)
    file_semesters = {item["semester"] for item in all_files if item.get("semester")}
    config_sem_keys = sort_semesters(list(semesters.keys()))
    semester_values = sort_semesters(list(set(config_sem_keys) | file_semesters))
    semester_buttons = '<button class="semester-option active" data-semester="all">All Semesters</button>'
    for sem in semester_values:
        label = semesters.get(sem, f"Semester {sem}")
        semester_buttons += f'<button class="semester-option" data-semester="{html.escape(sem)}">{html.escape(label)}</button>'

    contributors_json = json.dumps(contributors)
    year = datetime.datetime.now().year

    html_template = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\"> 
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>CSE Student Hub</title>
    <link rel=\"manifest\" href=\"manifest.json\">
    <meta name=\"theme-color\" content=\"#0B7285\">
    <link rel=\"icon\" href=\"https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png\"/>
    <link rel=\"stylesheet\" href=\"style.css\">
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Sora:wght@500;700&display=swap\" rel=\"stylesheet\">
    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js\" defer></script>
</head>
<body>
    <video autoplay loop muted playsinline class=\"main-page-bg-video\">
        <source src=\"bg.mp4\" type=\"video/mp4\">
    </video>

    <header>
        <div class=\"header-content\">
            <h1>CSE Student Hub</h1>
            <p>Pick your semester and jump to notes, assignments, and lab files.</p>
        </div>
        <div class=\"profile-area\">
            <img src=\"https://placehold.co/100x100/0b7285/FFFFFF?text=U\" alt=\"User Profile\" id=\"profile-pic\" class=\"profile-pic\">
        </div>
    </header>

    <main>
        <section class=\"semester-selector semester-hero\" aria-label=\"Semester selection\">
            <span class=\"semester-badge\">Step 1</span>
            <h2>Choose your semester</h2>
            <p class=\"semester-hint\" id=\"semesterHint\">Start here — pick your semester to see relevant notes, assignments, and lab files. You can switch anytime.</p>
            <div class=\"semester-options\" id=\"semester-options\">{semester_buttons}</div>
        </section>

        <section class=\"search-and-tabs\" aria-label=\"Filter and browse\">
            <div class=\"search-box\">
                <span class=\"search-icon\" aria-hidden=\"true\">⌕</span>
                <input class=\"search-input\" type=\"text\" placeholder=\"Filter by file name, course code, or keyword...\" id=\"searchBox\" autocomplete=\"off\">
            </div>
            <details class=\"advanced-filters\">
                <summary>Advanced Filters</summary>
                <div class=\"filter-grid\">
                    <select id=\"courseFilter\">
                        <option value=\"all\">All Courses</option>
                        {''.join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in sorted(set(i["course"] for i in all_files)))}
                    </select>
                    <select id=\"typeFilter\">
                        <option value=\"all\">All Types</option>
                        {''.join(f'<option value="{t}">{t.upper()}</option>' for t in sorted(set(i["ext"].lstrip(".") for i in all_files)))}
                    </select>
                    <select id=\"sortFilter\">
                        <option value=\"newest\">Newest First</option>
                        <option value=\"oldest\">Oldest First</option>
                        <option value=\"name\">Name A-Z</option>
                    </select>
                </div>
            </details>
            <div class=\"tabs\" role=\"tablist\">{tabs_html}</div>
        </section>

        {panels_html}
        <p id=\"no-results-message\" class=\"no-results-message hidden\" aria-live=\"polite\">No files match your semester or search. Try a different semester or keyword.</p>
    </main>

    <footer class=\"site-footer\">
        <div class=\"footer-content\">
            <div class=\"footer-section\"><h4>Share this Site</h4><p>Scan and open on mobile.</p><img class=\"qr-code\" src=\"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://shiroonigami23-ui.github.io/class-solutions/\" alt=\"QR Code for site\"/></div>
            <div class=\"footer-section\"><h4>Feedback & Requests</h4><p>Need a file or fix?</p><a href=\"https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header\" target=\"_blank\" class=\"feedback-button\">Let Us Know</a></div>
        </div>
        <div class=\"footer-bottom\"><p>&copy; {year} CSE Student Hub</p></div>
    </footer>

    <div id=\"profileModal\" class=\"modal-overlay\">
        <div class=\"modal-content\">
            <video autoplay loop muted playsinline class=\"profile-bg-video-full\">
                <source src=\"profile-bg.mp4\" type=\"video/mp4\">
            </video>

            <button class=\"close-modal-btn\" id=\"closeModalBtn\">&times;</button>

            <div class=\"profile-modal-header\">
                <div class=\"modal-profile-pic-wrapper\">
                    <img src=\"https://placehold.co/200x200/0b7285/FFFFFF?text=U\" alt=\"User Profile\" id=\"modal-profile-pic\" class=\"modal-profile-pic\">
                    <div class=\"modal-pic-overlay\"><span>Click to Upload</span></div>
                </div>
                <input type=\"file\" id=\"modal-pic-upload\" accept=\"image/*\" style=\"display: none;\">
                <h2 id=\"modal-profile-name\">Your Name</h2>
            </div>

            <div class=\"modal-tabs\">
                <button class=\"modal-tab-link active\" onclick=\"openProfileTab(event, 'settings')\">Settings</button>
                <button class=\"modal-tab-link\" onclick=\"openProfileTab(event, 'contribute')\">Your Contributions</button>
            </div>

            <div id=\"settings\" class=\"modal-tab-content\" style=\"display: block;\">
                <div class=\"setting-item\">
                    <label for=\"profile-name-input\">Display Name</label>
                    <input type=\"text\" id=\"profile-name-input\" placeholder=\"Enter your display name...\">
                </div>
                <div class=\"setting-item\">
                    <label for=\"github-username-input\">GitHub Username</label>
                    <input type=\"text\" id=\"github-username-input\" placeholder=\"e.g., shiroonigami23-ui\">
                </div>
                <div class=\"setting-item theme-toggle\">
                    <label>Theme</label>
                    <button id=\"modeBtn\">☀️</button>
                </div>
                <button id=\"save-profile-btn\" class=\"action-button primary\">Save Changes</button>
            </div>

            <div id=\"contribute\" class=\"modal-tab-content\">
                <h3>Your Submitted Files</h3>
                <div id=\"user-contributions-list\"></div>
                <a href=\"contribute.html\" class=\"action-button primary contribute-link\">Contribute a New File</a>
            </div>
        </div>
    </div>

    <div id=\"pdfPreviewModal\" class=\"modal-overlay pdf-preview-modal\">
        <div class=\"pdf-modal-content\">
            <button class=\"close-modal-btn\" id=\"closePdfModalBtn\">&times;</button>
            <h3 id=\"pdf-modal-title\"></h3>
            <div id=\"pdf-viewer-container\"><div id=\"loader\"></div><canvas id=\"pdf-canvas\"></canvas></div>
        </div>
    </div>

    <script>window.contributorsData = {contributors_json};</script>
    <script src=\"script.js\" defer></script>
    <script src=\"profile.js\" defer></script>
    <script src=\"preview.js\" defer></script>
    <script>
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/sw.js').catch(() => {{}});
            }});
        }}
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_template)

    print("SUCCESS: index.html generated with semester selector and YAML-aware course mapping.")


if __name__ == "__main__":
    main()
