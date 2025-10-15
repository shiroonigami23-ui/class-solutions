   main()
import os
import re
import datetime
import subprocess

# --- CONFIGURATION ---
SUPPORTED_EXTENSIONS = ['.pdf', '.epub']
IGNORE_FILES = ['README.md']

# New, robust keyword-based mapping for courses.
# The script will check if any of these (case-insensitive) keywords are in the filename.
COURSE_KEYWORDS = {
    'CS-501': ['toc', 'automata', 'nfa', 'cs501'],
    'CS-502': ['dbms', 'rdbms', 'database', 'cs502'],
    'CS-503': ['cyber', 'security', 'data', 'analytics', 'cs503'],
    'CS-504': ['internet', 'web', 'iwd', 'cs504']
}

def get_course_code(filename):
    """Categorizes a file based on keywords in its name."""
    fn_lower = filename.lower()
    for code, keywords in COURSE_KEYWORDS.items():
        if any(keyword in fn_lower for keyword in keywords):
            return code
    return 'Uncategorized' # Fallback if no keywords match

def get_file_creation_date(filepath):
    """Gets the creation date of a file in the git repo."""
    try:
        timestamp_str = subprocess.check_output(
            ['git', 'log', '--diff-filter=A', '--format=%at', '--', filepath]
        ).decode('utf-8').strip()
        if timestamp_str:
            latest_timestamp = int(timestamp_str.split('\n')[-1])
            return datetime.datetime.fromtimestamp(latest_timestamp)
    except Exception:
        pass # Fallback to filesystem time
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

def get_file_size(filepath):
    """Gets file size and returns a human-readable string."""
    size_bytes = os.path.getsize(filepath)
    if size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/1024**2:.2f} MB"

def format_title(filename):
    """Creates a clean, human-readable title from a filename."""
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
    title = re.sub(r'^(CS \d+\s*)', '', title, flags=re.IGNORECASE)
    return title.strip().title()

def generate_file_html(file_info):
    """Generates the HTML block for a single file."""
    title = format_title(file_info['name'])
    keywords = f"{title} {file_info['course']}"
    
    if file_info['ext'] == '.pdf':
        return f"""
        <div class="pdf-block file-row" data-keywords="{keywords}">
          <div class="pdf-title"><img class="icon" src="https://img.icons8.com/color/48/000000/pdf.png" alt="PDF icon"/>{title}</div>
          <div class="pdf-preview"><iframe class="pdf-frame" src="{file_info['name']}" loading="lazy" aria-label="Preview of {title}"></iframe></div>
          <div class="file-actions">
            <a href="{file_info['name']}" target="_blank" class="download-link" aria-label="Download {title}">Download PDF</a><span class="file-size">{file_info['size']}</span>
          </div>
        </div>"""
    elif file_info['ext'] == '.epub':
        return f"""
        <li class="file-row" data-keywords="{keywords}">
          <div class="file-info"><img class="icon" src="https://img.icons8.com/color/48/000000/book.png" alt="Book icon"/><span class="file-title">{title}</span></div>
          <div class="file-actions">
            <a href="{file_info['name']}" target="_blank" class="download-link" aria-label="Download {title}">Download EPUB</a><span class="file-size">{file_info['size']}</span>
          </div>
        </li>"""
    return ""

def main():
    """Main function to generate the index.html file."""
    all_files = []
    now = datetime.datetime.now()

    for filename in sorted(os.listdir('.')):
        if filename in IGNORE_FILES or filename.startswith('.'):
            continue
        file_ext = os.path.splitext(filename)[1]
        if file_ext in SUPPORTED_EXTENSIONS:
            all_files.append({
                'name': filename,
                'ext': file_ext,
                'size': get_file_size(filename),
                'date': get_file_creation_date(filename),
                'course': get_course_code(filename)
            })

    all_files.sort(key=lambda x: x['date'], reverse=True)

    new_files_banner_links = []
    for f in all_files:
        if (now - f['date']).total_seconds() < 48 * 3600:
            new_files_banner_links.append(f'<a href="{f["name"]}">{format_title(f["name"])}</a>')
            
    new_files_html = ' &mdash; '.join(new_files_banner_links)
    
    courses = sorted(list(set(f['course'] for f in all_files if f['course'] != 'Uncategorized')))
    if 'Uncategorized' in [f['course'] for f in all_files]:
        courses.append('Uncategorized')

    assignments_html = ""
    notes_html = "<ul class='file-list'>"
    for course in courses:
        assignments_html += f"<div class='course-title'>{course}</div>"
        has_epub_for_course = any(f['ext'] == '.epub' and f['course'] == course for f in all_files)
        if has_epub_for_course:
            notes_html += f"<div class='course-title'>{course}</div>"
        for f in all_files:
            if f['course'] == course:
                if f['ext'] == '.pdf':
                    assignments_html += generate_file_html(f)
                elif f['ext'] == '.epub':
                    notes_html += generate_file_html(f)
    notes_html += "</ul>"

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSE • Notes & Assignments</title>
    <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
    <link rel="stylesheet" href="style.css"><link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>CSE Notes & Assignments</h1><p class="desc">A centralized repository for CSE course materials. Easy to find, preview, and download.</p>
            <button class="darkmode-btn" id="modeBtn" aria-label="Toggle Dark/Light Mode">🌙</button>
        </div>
    </header>
    <main>
        <div class="new-banner" id="new-files-banner">
            <span class="new-emoji">✨</span><span id="new-files-content">{'<strong>Recently Added:</strong> ' + new_files_html if new_files_html else 'No new files in the last 48 hours.'}</span>
        </div>
        <div class="search-box"><input class="search-input" type="text" placeholder="Filter by name or course code..." oninput="filterFiles()" id="searchBox" aria-label="Filter files"></div>
        <div class="last-updated">Site last updated: <span id="lastUpdate"></span></div>
        <section id="assignments-section">
            <h2 class="section-title">Assignments (PDF)</h2><div class="grid-container" id="assignmentsGrid">{assignments_html}</div>
        </section>
        <section id="notes-section">
            <h2 class="section-title">Notes (EPUB)</h2><div class="list-container" id="notesList">{notes_html}</div>
        </section>
        <section class="feedback-section">
            <h2 class="section-title">Feedback / Request</h2>
            <a class="feedback-link" href="https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header" target="_blank">💬 Suggest improvements or request files</a>
        </section>
        <section class="qr-section">
            <h2 class="section-title">Share This Site</h2>
            <p>Scan the QR code below or long-press to save and share.</p>
            <img class="qr-img" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://shiroonigami23-ui.github.io/class-solutions/" alt="QR Code for the website"/>
        </section>
    </main>
    <footer><p>&copy; {datetime.datetime.now().year} Aryan Singh Chandel | All Rights Reserved</p></footer>
    <script src="script.js" defer></script>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("index.html has been successfully generated with improved categorization.")

if __name__ == '__main__':
    main()
