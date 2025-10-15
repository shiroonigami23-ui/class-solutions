import os
import re
import json
import datetime
import subprocess

# --- CONFIGURATION ---
SUPPORTED_EXTENSIONS = ['.pdf', '.epub', '.jpg', '.png', '.jpeg', '.txt', '.md']
# Add .meta so the script is aware of it, but it won't be displayed
IGNORE_FILES = ['README.md', 'generate_index.py', 'style.css', 'script.js', 'profile.js', 'preview.js', 'index.html', 'contribute.html', 'contribution_handler.js', 'contributors.json', 'update_contributors.py']
COURSE_KEYWORDS = {
    'CS-501': ['toc', 'automata', 'nfa', 'cs501'],
    'CS-502': ['dbms', 'rdbms', 'database', 'cs502'],
    'CS-503': ['cyber', 'security', 'data', 'analytics', 'cs503'],
    'CS-504': ['internet', 'web', 'iwd', 'cs504']
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

# --- HELPER FUNCTIONS ---

def load_contributors():
    try:
        with open('contributors.json', 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_course_code(filename):
    fn_lower = filename.lower();
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
    size = os.path.getsize(filepath);
    if size < 1024**2: return f"{size/1024:.1f} KB"
    return f"{size/1024**2:.2f} MB"

def format_title(filename):
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ');
    return re.sub(r'^(CS \d+\s*)', '', title, flags=re.IGNORECASE).strip().title()

# --- NEW: ADVANCED KEYWORD EXTRACTION ---
def extract_keywords(file_info):
    keywords = set()
    base_filename = os.path.splitext(file_info['name'])[0]
    meta_filepath = base_filename + '.meta'

    # Method 1: Check for a companion .meta file
    if os.path.exists(meta_filepath):
        with open(meta_filepath, 'r', encoding='utf-8') as f:
            keywords.update(f.read().lower().split())

    # Method 2: Read content from text-based files
    if file_info['ext'] in ['.txt', '.md']:
        try:
            with open(file_info['name'], 'r', encoding='utf-8') as f:
                # Read first 100 words
                content = f.read(500).lower() 
                # Basic cleanup
                words = re.findall(r'\b\w+\b', content)
                keywords.update(words)
        except Exception as e:
            print(f"Could not read {file_info['name']} for keywords: {e}")

    return ' '.join(list(keywords))

# --- GENERATE HTML ---
def generate_file_html(file_info, contributors):
    title = format_title(file_info['name'])
    base_keywords = f"{title} {file_info['course']}"
    content_keywords = extract_keywords(file_info)
    all_keywords = f"{base_keywords} {content_keywords}"

    contributor_name = contributors.get(file_info['name'])
    contributor_html = f'<div class="contributor-credit">Added by <a href="https://github.com/{contributor_name}" target="_blank">@{contributor_name}</a></div>' if contributor_name else ''
    
    # Add a preview button only for PDF files
    preview_button_html = ''
    if file_info['ext'] == '.pdf':
        preview_button_html = f'<button class="preview-button" data-pdf-url="{file_info["name"]}">Preview</button>'

    return f"""
    <div class="file-card file-row" data-keywords="{all_keywords}" data-course="{file_info['course']}">
        <div class="file-icon"><img src="{FILE_TYPE_MAP.get(file_info['ext'], {}).get('icon', '')}" alt="{file_info['ext']} icon"></div>
        <div class="file-details">
            <div class="file-title">{title}</div>
            <div class="file-meta">{file_info['course']} &bull; {file_info['size']}</div>
            {contributor_html}
        </div>
        <div class="file-actions">
            {preview_button_html}
            <a href="{file_info['name']}" target="_blank" class="download-button" aria-label="Download {title}">View</a>
        </div>
    </div>"""

# --- MAIN EXECUTION ---
def main():
    contributors = load_contributors()
    all_files = []
    for filename in sorted(os.listdir('.')):
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTENSIONS and filename not in IGNORE_FILES and not filename.startswith('.'):
            all_files.append({'name': filename, 'ext': ext, 'size': get_file_size(filename), 'date': get_file_creation_date(filename), 'course': get_course_code(filename)})
    
    all_files.sort(key=lambda x: x['date'], reverse=True)
    
    content_by_category = {v['category']: '' for v in FILE_TYPE_MAP.values()}; content_by_category['All Files'] = ''
    for f in all_files:
        html_card = generate_file_html(f, contributors)
        content_by_category['All Files'] += html_card
        category = FILE_TYPE_MAP.get(f['ext'], {}).get('category')
        if category in content_by_category: content_by_category[category] += html_card
        
    tabs_html, panels_html = "", ""
    ordered_categories = ['All Files'] + sorted([c for c in content_by_category if c != 'All Files'])
    for category in ordered_categories:
        content = content_by_category.get(category, '');
        if content:
            id_name = category.replace(' ', '');
            tabs_html += f'<button class="tab-link" onclick="openTab(event, \'{id_name}\')">{category}</button>'
            panels_html += f'<div id="{id_name}" class="tab-content"><div class="file-grid">{content}</div></div>'
            
    contributors_json = json.dumps(contributors)

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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js" defer></script>
</head>
<body>
    <header>
        <div class="header-content"><h1>CSE Student Hub</h1><p>Your central dashboard for notes, assignments, and resources.</p></div>
        <div class="profile-area"><img src="https://placehold.co/100x100/7c3aed/FFFFFF?text=U" alt="User Profile" id="profile-pic" class="profile-pic"></div>
    </header>
    <main>
        <div class="search-and-tabs"><div class="search-box"><input class="search-input" type="text" placeholder="Filter files by name or course..." id="searchBox" oninput="filterFiles()"></div><div class="tabs">{tabs_html}</div></div>
        {panels_html}
    </main>
    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-section"><h4>Share this Site</h4><p>Scan the QR code with your phone.</p><img class="qr-code" src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://shiroonigami23-ui.github.io/class-solutions/" alt="QR Code for site"/></div>
            <div class="footer-section"><h4>Feedback & Requests</h4><p>Have a suggestion or need a file?</p><a href="https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header" target="_blank" class="feedback-button">Let Us Know</a></div>
        </div>
        <div class="footer-bottom"><p>&copy; {datetime.datetime.now().year} Aryan Singh Chandel | Enhanced Edition</p></div>
    </footer>

    <!-- Profile Modal (Structure remains the same) -->
    <div id="profileModal" class="modal-overlay">
        <div class="modal-content">
            <button class="close-modal-btn" id="closeModalBtn">&times;</button>
            <div class="profile-modal-header">
                <div class="profile-modal-banner"></div>
                <div class="modal-profile-pic-wrapper"><img src="https://placehold.co/200x200/7c3aed/FFFFFF?text=U" alt="User Profile" id="modal-profile-pic" class="modal-profile-pic"><div class="modal-pic-overlay"><span>Click to Upload</span></div></div>
                <input type="file" id="modal-pic-upload" accept="image/*" style="display: none;">
                <h2 id="modal-profile-name">Your Name</h2>
            </div>
            <div class="modal-tabs">
                <button class="modal-tab-link active" onclick="openProfileTab(event, 'settings')">Settings</button>
                <button class="modal-tab-link" onclick="openProfileTab(event, 'contribute')">Your Contributions</button>
            </div>
            <div id="settings" class="modal-tab-content" style="display: block;">
                <div class="setting-item"><label for="profile-name-input">Display Name</label><input type="text" id="profile-name-input" placeholder="Enter your display name..."></div>
                <div class="setting-item"><label for="github-username-input">GitHub Username</label><input type="text" id="github-username-input" placeholder="e.g., shiroonigami23-ui"></div>
                <div class="setting-item theme-toggle"><label>Theme</label><button id="modeBtn">☀️</button></div>
                <button id="save-profile-btn" class="action-button primary">Save Changes</button>
            </div>
            <div id="contribute" class="modal-tab-content">
                <h3>Your Submitted Files</h3><div id="user-contributions-list"></div>
                <a href="contribute.html" class="action-button primary contribute-link">Contribute a New File</a>
            </div>
        </div>
    </div>
    
    <!-- PDF Preview Modal -->
    <div id="pdfPreviewModal" class="modal-overlay pdf-preview-modal">
        <div class="pdf-modal-content">
            <button class="close-modal-btn" id="closePdfModalBtn">&times;</button>
            <h3 id="pdf-modal-title"></h3>
            <div id="pdf-viewer-container"><div id="loader"></div><canvas id="pdf-canvas"></canvas></div>
        </div>
    </div>
    
    <script> window.contributorsData = {contributors_json}; </script>
    <script src="script.js" defer></script>
    <script src="profile.js" defer></script>
    <script src="preview.js" defer></script>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f: f.write(html_template)
    print("SUCCESS: index.html generated with PDF Preview and Smart Search capabilities.")

if __name__ == '__main__':
    main()
