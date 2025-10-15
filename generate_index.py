   main()
import os
import re
import datetime
import subprocess

# --- CONFIGURATION ---
SUPPORTED_EXTENSIONS = ['.pdf', '.epub', '.jpg', '.png', '.jpeg', '.txt', '.md']
IGNORE_FILES = ['README.md']

# Flexible keyword-based mapping for courses.
COURSE_KEYWORDS = {
    'CS-501': ['toc', 'automata', 'nfa', 'cs501'],
    'CS-502': ['dbms', 'rdbms', 'database', 'cs502'],
    'CS-503': ['cyber', 'security', 'data', 'analytics', 'cs503'],
    'CS-504': ['internet', 'web', 'iwd', 'cs504']
}
# Mapping file extensions to their display category and icon
FILE_TYPE_MAP = {
    '.pdf': {'category': 'Documents', 'icon': 'https://img.icons8.com/fluency/48/adobe-pdf.png'},
    '.epub': {'category': 'Notes', 'icon': 'https://img.icons8.com/fluency/48/book.png'},
    '.jpg': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.jpeg': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.png': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.txt': {'category': 'Text Files', 'icon': 'https://img.icons8.com/fluency/48/document.png'},
    '.md': {'category': 'Text Files', 'icon': 'https://img.icons8.com/fluency/48/document.png'}
}

def get_course_code(filename):
    fn_lower = filename.lower()
    for code, keywords in COURSE_KEYWORDS.items():
        if any(keyword in fn_lower for keyword in keywords):
            return code
    return 'Uncategorized'

def get_file_creation_date(filepath):
    try:
        ts_str = subprocess.check_output(['git', 'log', '--diff-filter=A', '--format=%at', '--', filepath]).decode().strip()
        if ts_str: return datetime.datetime.fromtimestamp(int(ts_str.split('\n')[-1]))
    except: pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

def get_file_size(filepath):
    size = os.path.getsize(filepath)
    if size < 1024**2: return f"{size/1024:.1f} KB"
    return f"{size/1024**2:.2f} MB"

def format_title(filename):
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
    return re.sub(r'^(CS \d+\s*)', '', title, flags=re.IGNORECASE).strip().title()

def generate_file_html(file_info):
    title = format_title(file_info['name'])
    keywords = f"{title} {file_info['course']}"
    icon_url = FILE_TYPE_MAP.get(file_info['ext'], {}).get('icon', '')

    return f"""
    <div class="file-card file-row" data-keywords="{keywords}" data-course="{file_info['course']}">
        <div class="file-icon"><img src="{icon_url}" alt="{file_info['ext']} icon"></div>
        <div class="file-details">
            <div class="file-title">{title}</div>
            <div class="file-meta">{file_info['course']} &bull; {file_info['size']}</div>
        </div>
        <a href="{file_info['name']}" target="_blank" class="download-button" aria-label="Download {title}">View</a>
    </div>
    """

def main():
    all_files = []
    now = datetime.datetime.now()
    for filename in sorted(os.listdir('.')):
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTENSIONS and filename not in IGNORE_FILES and not filename.startswith('.'):
            all_files.append({
                'name': filename, 'ext': ext, 'size': get_file_size(filename),
                'date': get_file_creation_date(filename), 'course': get_course_code(filename)
            })
    all_files.sort(key=lambda x: x['date'], reverse=True)

    # --- Generate HTML for different tabs ---
    content_by_category = {cat_info['category']: '' for cat_info in FILE_TYPE_MAP.values()}
    content_by_category['All Files'] = ''
    
    for f in all_files:
        html_card = generate_file_html(f)
        content_by_category['All Files'] += html_card
        category = FILE_TYPE_MAP.get(f['ext'], {}).get('category')
        if category:
            content_by_category[category] += html_card

    # --- Build the final HTML page ---
    tabs_html = ""
    panels_html = ""
    for category, content in content_by_category.items():
        if content: # Only create a tab if there is content for it
            id_name = category.replace(' ', '')
            tabs_html += f'<button class="tab-link" onclick="openTab(event, \'{id_name}\')">{category}</button>'
            panels_html += f'<div id="{id_name}" class="tab-content"><div class="file-grid">{content}</div></div>'

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSE Student Hub</title>
    <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png"/>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>CSE Student Hub</h1>
            <p>Your central dashboard for notes, assignments, and resources.</p>
        </div>
        <div class="profile-area">
            <img src="https://placehold.co/100x100/7c3aed/FFFFFF?text=U" alt="User Profile" id="profile-pic" class="profile-pic">
            <div class="profile-dropdown" id="profile-dropdown">
                <div class="profile-header">
                    <img src="https://placehold.co/100x100/7c3aed/FFFFFF?text=U" alt="User Profile" id="dropdown-profile-pic">
                    <div class="profile-info">
                        <span id="profile-name-display">Your Name</span>
                        <label for="profile-pic-upload" class="change-avatar-btn">Change Avatar</label>
                        <input type="file" id="profile-pic-upload" accept="image/*" style="display: none;">
                    </div>
                </div>
                <div class="profile-actions">
                    <input type="text" id="profile-name-input" placeholder="Enter your name...">
                    <button id="save-profile-btn">Save Profile</button>
                    <div class="theme-toggle">
                        <span>Theme</span>
                        <button id="modeBtn">☀️</button>
                    </div>
                </div>
            </div>
        </div>
    </header>
    <main>
        <div class="search-and-tabs">
            <div class="search-box">
                <input class="search-input" type="text" placeholder="Filter files by name or course..." id="searchBox" oninput="filterFiles()">
            </div>
            <div class="tabs">
                {tabs_html}
            </div>
        </div>
        {panels_html}
    </main>
    <footer><p>&copy; {datetime.datetime.now().year} Aryan Singh Chandel | Enhanced Edition</p></footer>
    <script src="script.js" defer></script>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("index.html successfully generated with new professional layout and profile section.")

if __name__ == '__main__':
    main()
