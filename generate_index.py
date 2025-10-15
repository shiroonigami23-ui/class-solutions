import os
import re
import datetime
import subprocess

# --- CONFIGURATION ---
# Add file extensions you want to include in the index.
SUPPORTED_EXTENSIONS = ['.pdf', '.epub']
# Files to ignore completely.
IGNORE_FILES = ['README.md']
# Course code mapping based on filename prefixes.
COURSE_MAPPING = {
    'TOC_': 'CS-501',
    'DBMS_': 'CS-502',
    'Data_Analytics_': 'CS-503',
    '_CS_503_': 'CS-503', # Handles your new file format
    'Internet_and_Web_': 'CS-504',
}

def get_file_creation_date(filepath):
    """Gets the creation date of a file in the git repo."""
    try:
        # Get the UNIX timestamp of the first commit for the file
        timestamp_str = subprocess.check_output(
            ['git', 'log', '--diff-filter=A', '--format=%at', '--', filepath]
        ).decode('utf-8').strip()
        
        if timestamp_str:
            # The command can sometimes return multiple timestamps if a file was deleted and re-added.
            # We take the most recent "add" timestamp, which is the last one.
            latest_timestamp = int(timestamp_str.split('\n')[-1])
            return datetime.datetime.fromtimestamp(latest_timestamp)
    except Exception as e:
        print(f"Warning: Could not get git creation date for {filepath}. Error: {e}")
    # Fallback to filesystem modification time if git fails
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

def get_file_size(filepath):
    """Gets file size and returns a human-readable string (KB or MB)."""
    size_bytes = os.path.getsize(filepath)
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/1024**2:.2f} MB"

def format_title(filename):
    """Creates a clean, human-readable title from a filename."""
    # Remove extension and replace underscores/hyphens with spaces
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
    # Remove common prefixes/suffixes for a cleaner look
    title = re.sub(r'^(CS \d+\s*)', '', title, flags=re.IGNORECASE)
    return title.strip().title()

def generate_file_html(file_info):
    """Generates the HTML block for a single file."""
    title = format_title(file_info['name'])
    keywords = f"{title} {file_info['course']}"
    
    if file_info['ext'] == '.pdf':
        return f"""
        <div class="pdf-block file-row" data-keywords="{keywords}">
          <div class="pdf-title">
            <img class="icon" src="https://img.icons8.com/color/48/000000/pdf.png" alt="PDF icon"/>
            {title}
          </div>
          <div class="pdf-preview">
            <iframe class="pdf-frame" src="{file_info['name']}" loading="lazy" aria-label="Preview of {title}"></iframe>
          </div>
          <div class="file-actions">
            <a href="{file_info['name']}" target="_blank" class="download-link" aria-label="Download {title}">Download PDF</a>
            <span class="file-size">{file_info['size']}</span>
          </div>
        </div>
        """
    elif file_info['ext'] == '.epub':
        return f"""
        <li class="file-row" data-keywords="{keywords}">
          <div class="file-info">
            <img class="icon" src="https://img.icons8.com/color/48/000000/book.png" alt="Book icon"/>
            <span class="file-title">{title}</span>
          </div>
          <div class="file-actions">
            <a href="{file_info['name']}" target="_blank" class="download-link" aria-label="Download {title}">Download EPUB</a>
            <span class="file-size">{file_info['size']}</span>
          </div>
        </li>
        """
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
            creation_date = get_file_creation_date(filename)
            course_code = 'Uncategorized'
            for prefix, code in COURSE_MAPPING.items():
                if filename.startswith(prefix):
                    course_code = code
                    break
            
            all_files.append({
                'name': filename,
                'ext': file_ext,
                'size': get_file_size(filename),
                'date': creation_date,
                'course': course_code
            })

    # Sort files by creation date, newest first
    all_files.sort(key=lambda x: x['date'], reverse=True)

    # --- Generate HTML Sections ---
    new_files_banner_links = []
    # A file is "new" if it was added in the last 2 days (48 hours)
    for f in all_files:
        if (now - f['date']).total_seconds() < 48 * 3600:
            new_files_banner_links.append(f'<a href="{f["name"]}">{f["name"]}</a>')
            
    new_files_html = ' &mdash; '.join(new_files_banner_links)
    
    courses = sorted(list(set(f['course'] for f in all_files)))
    assignments_html = ""
    notes_html = "<ul class='file-list'>"

    for course in courses:
        # Add course title for assignments
        assignments_html += f"<div class='course-title'>{course}</div>"
        
        # Add course title for notes (EPUBs)
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

    # --- HTML Template ---
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSE • Notes & Assignments</title>
    <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>CSE Notes & Assignments</h1>
            <p class="desc">A centralized repository for CSE course materials. Easy to find, preview, and download.</p>
            <button class="darkmode-btn" id="modeBtn" aria-label="Toggle Dark/Light Mode">🌙</button>
        </div>
    </header>

    <main>
        <div class="new-banner" id="new-files-banner">
            <span class="new-emoji">✨</span> 
            <span id="new-files-content">
                {'<strong>Recently Added:</strong> ' + new_files_html if new_files_html else 'No new files in the last 48 hours.'}
            </span>
        </div>
        
        <div class="search-box">
            <input class="search-input" type="text" placeholder="Filter by name or course code..." oninput="filterFiles()" id="searchBox" aria-label="Filter files">
        </div>
        
        <div class="last-updated">Site last updated: <span id="lastUpdate"></span></div>

        <section id="assignments-section">
            <h2 class="section-title">Assignments (PDF)</h2>
            <div class="grid-container" id="assignmentsGrid">
                {assignments_html}
            </div>
        </section>

        <section id="notes-section">
            <h2 class="section-title">Notes (EPUB)</h2>
            <div class="list-container" id="notesList">
                {notes_html}
            </div>
        </section>
        
        <section class="feedback-section">
            <h2 class="section-title">Feedback / Request</h2>
            <a class="feedback-link" href="https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header" target="_blank">💬 Suggest improvements or request files</a>
        </section>
    </main>

    <footer>
        <p>&copy; {datetime.datetime.now().year} Aryan Singh Chandel | All Rights Reserved</p>
    </footer>

    <script src="script.js" defer></script>
</body>
</html>
    """

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("index.html has been successfully generated.")

if __name__ == '__main__':
    main()
