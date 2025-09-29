#!/usr/bin/env python3
import os
import re
import time
from datetime import datetime, timedelta
from urllib.parse import quote

# Config
ROOT = "."
INDEX_FILE = "index.html"
NEW_DAYS = 3  # banner shows files with mtime within this many days

# Regex to detect course codes like CS-501 or CS_501 or CS501 (we normalize to CS-501)
COURSE_REGEX = re.compile(r"(CS[-_]?\d{3})", re.IGNORECASE)


def extract_course_code(filename):
    """Return normalized course code like 'CS-501' or 'CS-000' if none found."""
    m = COURSE_REGEX.search(filename)
    if not m:
        return "CS-000"
    code = m.group(1).upper().replace("_", "-")
    # ensure pattern like CS-501
    if not code.startswith("CS-") and code.startswith("CS"):
        code = "CS-" + code[2:]
    return code


def format_size(path):
    """Return human-friendly size string for a file (KB/MB)."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return "0 B"
    if size < 1024:
        return f"{size} B"
    kb = size / 1024.0
    if kb < 1024:
        return f"{kb:.1f} KB"
    mb = kb / 1024.0
    return f"{mb:.2f} MB"


def safe_title(filename):
    """Return display title from filename (no extension, underscores to spaces)."""
    title = os.path.splitext(os.path.basename(filename))[0]
    return title.replace("_", " ").strip()


def build_pdf_section(grouped_pdfs):
    """Return HTML for Assignments (PDF) grouped by course code."""
    out = []
    for code in sorted(grouped_pdfs.keys()):
        out.append(f'        <div class="course-title">{code}</div>')
        for f in sorted(grouped_pdfs[code]):
            title = safe_title(f)
            size = format_size(f)
            # safe id for JS if needed
            safe_id = re.sub(r'\W+', '', title.lower())
            # keywords for filter: title, code, variations
            last_part = code.split('-')[1] if '-' in code else code
            keywords = f"{title} {code} {code.lower()} {code.replace('-', '')} {last_part}"
            href = quote(f)
            block = f'''
        <div class="pdf-block fileRow" data-keywords="{keywords}">
          <div class="pdf-title"><img class="icon" src="https://img.icons8.com/color/48/000000/pdf.png" alt="PDF icon"/>{title}</div>
          <iframe class="pdf-frame" src="{href}" aria-label="View {title}"></iframe><br>
          <a href="{href}" target="_blank" class="download-link" aria-label="Download {title}">Download PDF</a>
          <span class="file-size">({size})</span>
        </div>'''
            out.append(block)
    return "\n".join(out)


def build_epub_section(grouped_epubs):
    """Return HTML for Notes (EPUB) grouped by course code."""
    out = []
    for code in sorted(grouped_epubs.keys()):
        out.append(f'          <div class="course-title">{code}</div>')
        for f in sorted(grouped_epubs[code]):
            title = safe_title(f)
            size = format_size(f)
            safe_id = re.sub(r'\W+', '', title.lower())
            last_part = code.split('-')[1] if '-' in code else code
            keywords = f"{title} {code} {code.lower()} {code.replace('-', '')} {last_part}"
            href = quote(f)
            block = f'''
        <li class="fileRow" data-keywords="{keywords}">
          <div class="left"><img class="icon" src="https://img.icons8.com/color/48/000000/book.png" alt="Book icon"/>{title}</div>
          <div>
            <a href="{href}" target="_blank" class="download-link" aria-label="Download {title}">Download</a>
            <span class="file-size">({size})</span>
            <div class="epub-msg">Use Moon+ Reader or any EPUB reader app.</div>
          </div>
        </li>'''
            out.append(block)
    return "\n".join(out)


def main():
    # collect files in repo root
    files = [f for f in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT, f))]
    pdfs = [f for f in files if f.lower().endswith(".pdf")]
    epubs = [f for f in files if f.lower().endswith(".epub")]

    # group by course code
    grouped_pdfs = {}
    for f in sorted(pdfs):
        code = extract_course_code(f)
        grouped_pdfs.setdefault(code, []).append(f)

    grouped_epubs = {}
    for f in sorted(epubs):
        code = extract_course_code(f)
        grouped_epubs.setdefault(code, []).append(f)

    # determine recent files (mtime within NEW_DAYS)
    recent = []
    cutoff = time.time() - (NEW_DAYS * 86400)
    for f in sorted(files):
        try:
            if os.path.getmtime(f) >= cutoff:
                # only include downloadable types (pdf/epub) and ignore things like workflow files
                if f.lower().endswith((".pdf", ".epub", ".txt", ".md")):
                    recent.append(f)
        except OSError:
            continue

    # build banner (blue style)
    banner_html = ""
    if recent:
        links = " — ".join([f'<a href="{quote(f)}">{f}</a>' for f in recent])
        banner_html = f'''
  <div class="new-banner">🆕 New files added: {links}</div>'''

    # build sections html
    pdf_section_html = build_pdf_section(grouped_pdfs)
    epub_section_html = build_epub_section(grouped_epubs)

    # final HTML (keeps your original layout & JS; file sizes rendered server-side)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSE • Notes & Assignments</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
  <style>
    body { background: #181e26; color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; min-height: 100vh; text-align: center; transition: background .3s, color .3s;}
    .lightmode { background: #f6f7f9; color: #232333;}
    .darkmode-btn { position:fixed;top:13px;right:13px;padding:6px 14px;font-size:1em;background:#253168;color:#f6f7f9;border:none;border-radius:20px;cursor:pointer;z-index:10; transition:.2s; box-shadow:0 1px 5px #0001;}
    h1 { font-size:2.11rem;margin:30px 0 6px 0;}
    .desc { color:#b5bac2; margin-bottom:4px; font-size:1.01em;}
    .update-bar {background:#21396c; color:#e3ecfd; margin:20px auto 18px; padding:7px 22px; font-size:.99em; border-radius:13px; max-width:570px;}
    .new-banner {background: #243b66; color: #e6f1ff; margin: 20px auto 14px; padding: 9px 16px; border-radius: 10px; max-width: 640px; box-shadow: 0 2px 8px rgba(0,0,0,0.35); font-size: 0.97em;}
    .new-banner a {color: #63b3ff; text-decoration: none; font-weight: 500;}
    .new-banner a:hover {text-decoration: underline; color: #8fd0ff;}
    main { max-width:700px;padding:0 8px;margin: 0 auto; }
    .search-box {margin:15px 0;}
    .search-input{padding:9px 14px;font-size:1.04em;width:72%;max-width:285px;border-radius:6px;border:1px solid #374b63;background:#21293b;color:#f6f7f9;}
    .last-updated{margin:4px auto 18px;font-size:.94em;color:#8dacbe;}
    .collapse-btn { margin:0 auto 3px;display:block;padding:7px 20px;font-size:1.01em;background:#183478;color:#dbe7fa;border:none;border-radius:9px;cursor:pointer;transition:.2s;}
    section {margin:32px 0 16px 0;}
    .section-title {margin-bottom:11px;font-size:1.11rem;text-transform:uppercase;letter-spacing:.7px;}
    .course-title {margin:15px 0 8px;font-size:1.05rem;color:#8adcff;}
    .pdf-block {margin:26px 0;background:#232b36;border-radius:13px;padding:18px 10px 13px;box-shadow:0 2.5px 9px #0003;}
    .pdf-title {font-size:1.08em; margin-bottom:10px; display:flex;align-items:center;justify-content:center;}
    .pdf-title .icon {width:19px;height:19px;margin-right:8px;}
    .pdf-frame {width:99%;max-width:660px;height:340px;border:1.5px solid #313141;border-radius:8px;background:#111015;margin-bottom:10px;}
    .download-link {display:inline-block; background:#203048;color:#8adcff;text-decoration:none;font-weight:500;font-size:1em; border-radius:8px;padding:6px 19px;transition:background .15s;box-shadow:0 1px 3.5px #0bf2;}
    .download-link:hover {background:#1e2a39;color:#b7f3ff;}
    .file-size {font-size:.95em;color:#bbe1d7;margin-left:9px;}
    .file-list {list-style:none;padding:0;margin:13px 0;}
    .file-list li { margin:9px 0; padding:9px 8px; background:#232b36; border-radius:9px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;box-shadow:0 1.5px 7px #0001;}
    .file-list .left {display:flex;align-items:center;}
    .file-list .icon {width:18px;height:18px;margin-right:7px;}
    .epub-msg {font-size:.9em;color:#aef1bb;margin-top:2px;}
    .footer {margin:38px 0 14px 0;opacity:.61;font-size:.97em;}
    .feedback {background:#21396c;color:#e8f2fa;font-size:.98em;padding:7px 16px;border-radius:7px;display:inline-block;margin-top:10px;text-decoration:none;}
    .qr-section {margin: 23px 0;}
    .qr-img {width:108px;display:block;margin:7px auto;}
    @media (max-width:700px) {
      .pdf-frame {height:39vw;min-height:150px;}
      .file-list li {flex-direction: column;align-items:flex-start;}
      .file-list .left {margin-bottom:7px;}
    }
  </style>
</head>
<body>
  <button class="darkmode-btn" id="modeBtn" aria-label="Toggle Dark/Light Mode">🌙</button>
  <h1 title="Assignments & Notes Repository">CSE Notes & Assignments</h1>
  <div class="desc">Instant download and reading for CSE students. All Assignment and Notes for you guys 😉!</div>""" + banner_html + """
  <div class="update-bar" id="update-bar">📢 Latest updates ( <span id="today"></span> )</div>
  <div class="last-updated">Last updated: <span id="lastUpdate"></span></div>
  <main>
    <div class="search-box">
      <input class="search-input" type="text" placeholder="Type to filter assignments/notes..." oninput="filterFiles()" id="searchBox" aria-label="Filter files">
    </div>
    <section>
      <button class="collapse-btn" type="button" onclick="toggleSection('assignmentsSection')">Assignments (PDF) ⬇️</button>
      <div id="assignmentsSection">
""" + pdf_section_html + """
      </div>
    </section>
    <section>
      <button class="collapse-btn" type="button" onclick="toggleSection('notesSection')">Notes (EPUB) ⬇️</button>
      <div id="notesSection">
        <ul class="file-list">""" + epub_section_html + """
        </ul>
      </div>
    </section>
    <div class="qr-section">
      <div style="margin-bottom:6px;font-size:1em;">Share this site: <br>Scan QR (or long-press to save)</div>
      <img class="qr-img" src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://shiroonigami23-ui.github.io/class-solutions/" alt="QR for site"/>
    </div>
    <section>
      <div class="section-title">Feedback / Request</div>
      <a class="feedback" href="https://docs.google.com/forms/d/e/1FAIpQLSedLRFNBdVoLSR0xfGk0iPJLp3UpRNEXlEhFrt9do0OYJf5_w/viewform?usp=header" target="_blank">💬 Suggest improvements or request files</a>
    </section>
    <div class="footer">&copy; Aryan Singh Chandel | CSE Section-A, 2025</div>
  </main>

  <script>
    function toggleSection(sectionId) {
      var s = document.getElementById(sectionId);
      if (s.style.display === "none") s.style.display = "block";
      else s.style.display = "none";
    }
    document.getElementById('assignmentsSection').style.display = "block";
    document.getElementById('notesSection').style.display = "block";
    let mode = localStorage.getItem("mode") || "dark";
    function setMode(m) {
      if(m==="light") {
        document.body.classList.add("lightmode");
        document.getElementById('modeBtn').textContent="🌞";
      } else {
        document.body.classList.remove("lightmode");
        document.getElementById('modeBtn').textContent="🌙";
      }
      localStorage.setItem("mode", m);
    }
    setMode(mode);
    document.getElementById('modeBtn').onclick = function() {
      mode = (mode === "dark") ? "light" : "dark";
      setMode(mode);
    };

    var update = new Date(document.lastModified);
    document.getElementById("lastUpdate").textContent = update.toLocaleDateString() + " " + update.toLocaleTimeString();
    document.getElementById("today").textContent = update.toLocaleDateString();

    function filterFiles() {
      let v = document.getElementById('searchBox').value.toLowerCase();
      document.querySelectorAll('.fileRow').forEach(function(row) {
        let keys = row.getAttribute('data-keywords') || '';
        row.style.display = (keys.toLowerCase().includes(v) || v === "") ? "" : "none";
      });
    }
  </script>
</body>
</html>
"""

    # write out the generated index.html
    with open(INDEX_FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"✅ {INDEX_FILE} generated. PDFs: {len(pdfs)}, EPUBs: {len(epubs)}, recent: {len(recent)}")


if __name__ == "__main__":
    main()
    
