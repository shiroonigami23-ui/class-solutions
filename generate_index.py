import os
import re
import datetime
import subprocess

# --- CONFIGURATION ---
SUPPORTED_EXTENSIONS = ['.pdf', '.epub', '.jpg', '.png', '.jpeg', '.txt', '.md']
IGNORE_FILES = ['README.md', 'generate_index.py', 'style.css', 'script.js', 'profile.js', 'index.html']

COURSE_KEYWORDS = {
    'CS-501': ['toc', 'automata', 'nfa', 'dfa', 'conversion dfa', 'cs501'],
    'CS-502': ['dbms', 'rdbms', 'database', 'cs502'],
    'CS-503': ['cyber', 'security', 'data', 'analytics', 'cs503'],
    'CS-504': ['internet', 'web', 'webpage', 'website', 'iwd', 'cs504']
}
FILE_TYPE_MAP = {
    '.pdf': {'category': 'Documents', 'icon': 'https://img.icons8.com/fluency/48/adobe-pdf.png'},
    '.epub': {'category': 'Notes', 'icon': 'https://img.icons8.com/fluency/48/book.png'},
    '.jpg': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.jpeg': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.png': {'category': 'Images', 'icon': 'https://img.icons8.com/fluency/48/image.png'},
    '.txt': {'category': 'Text Files', 'icon': 'https://img.icons8.com/fluency/48/document.png'},
    '.md': {'category': 'Text Files', 'icon': 'https://img.icons8.com/fluency/48/document.png'}
}

# --- (All the functions from before remain the same) ---
def get_course_code(filename):
    fn_lower = filename.lower()
    for code, keywords in COURSE_KEYWORDS.items():
        if any(keyword in fn_lower for keyword in keywords): return code
    return 'Uncategorized'

def get_file_creation_date(filepath):
    try:
        ts_str = subprocess.check_output(['git', 'log', '--diff-filter=A', '--format=%at', '--', filepath]).decode().strip()
        if ts_str: return datetime.datetime.fromtimestamp(int(ts_str.split('\n')[-1]))
    except Exception: pass
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
    </div>"""

def main():
    # --- (The file scanning and HTML generation logic is the same) ---
    all_files = []
    for filename in sorted(os.listdir('.')):
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTENSIONS and filename not in IGNORE_FILES and not filename.startswith('.'):
            all_files.append({
                'name': filename, 'ext': ext, 'size': get_file_size(filename),
                'date': get_file_creation_date(filename), 'course': get_course_code(filename)
            })
    all_files.sort(key=lambda x: x['date'], reverse=True)

    content_by_category = {cat_info['category']: '' for cat_info in FILE_TYPE_MAP.values()}
    content_by_category['All Files'] = ''
    for f in all_files:
        html_card = generate_file_html(f)
        content_by_category['All Files'] += html_card
        category = FILE_TYPE_MAP.get(f['ext'], {}).get('category')
        if category and category in content_by_category:
            content_by_category[category] += html_card

    tabs_html, panels_html = "", ""
    ordered_categories = ['All Files'] + sorted([cat for cat in content_by_category if cat != 'All Files'])
    for category in ordered_categories:
        content = content_by_category.get(category, '')
        if content:
            id_name = category.replace(' ', '')
            tabs_html += f'<button class="tab-link" onclick="openTab(event, \'{id_name}\')">{category}</button>'
            panels_html += f'<div id="{id_name}" class="tab-content"><div class="file-grid">{content}</div></div>'
    
    # --- THIS IS THE UPDATED HTML TEMPLATE ---
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSE Student Hub</title>
    <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png"/>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-content"><h1>CSE Student Hub</h1><p>Your central dashboard for notes, assignments, and resources.</p></div>
        <div class="profile-area"><img src="https://placehold.co/100x100/7c3aed/FFFFFF?text=U" alt="User Profile" id="profile-pic" class="profile-pic"></div>
    </header>
    <main>
        <div class="search-and-tabs">
            <div class="search-box"><input class="search-input" type="text" placeholder="Filter files by name or course..." id="searchBox" oninput="filterFiles()"></div>
            <div class="tabs">{tabs_html}</div>
        </div>
        {panels_html}
    </main>

    <!-- ==== NEW FOOTER SECTION ==== -->
    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>Share this Site</h4>
                <p>Scan the QR code with your phone.</p>
                <img class="qr-code" src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://shiroonigami23-ui.github.io/class-solutions/" alt="QR Code for site"/>
            </div>
            <div class="footer-section">
                <h4>Feedback & Requests</h4>
                <p>Have a suggestion or need a file?</p>
                <a href="https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header" target="_blank" class="feedback-button">Let Us Know</a>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; {datetime.datetime.now().year} Aryan Singh Chandel | Enhanced Edition</p>
        </div>
    </footer>
    
    <!-- Profile Modal Structure -->
    <div id="profileModal" class="modal-overlay">
        <div class="modal-content">
            <button class="close-modal-btn" id="closeModalBtn">&times;</button>
            <h2>Profile & Settings</h2>
            <div class="profile-modal-body">
                <div class="profile-pic-container">
                    <img src="https://placehold.co/200x200/7c3aed/FFFFFF?text=U" alt="User Profile" id="modal-profile-pic">
                    <label for="modal-pic-upload" class="change-avatar-btn-modal">Change Picture</label>
                    <input type="file" id="modal-pic-upload" accept="image/*" style="display: none;">
                </div>
                <div class="profile-settings">
                    <div class="setting-item">
                        <label for="profile-name-input">Your Name</label>
                        <input type="text" id="profile-name-input" placeholder="Enter your name...">
                    </div>
                    <div class="setting-item theme-toggle">
                        <label>Theme</label>
                        <button id="modeBtn">☀️</button>
                    </div>
                    <button id="save-profile-btn">Save Profile</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="script.js" defer></script>
    <script src="profile.js" defer></script>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f: f.write(html_template)
    print("SUCCESS: index.html generated with restored QR and Feedback sections in the footer.")

if __name__ == '__main__':
    main()
