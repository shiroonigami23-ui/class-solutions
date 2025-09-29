import os
import re
import datetime

ROOT = "."
OUTPUT_FILE = "index.html"
META_FILE = ".file_timestamps"

ALLOWED_ASSIGN_EXT = {".pdf"}
ALLOWED_NOTES_EXT = {".epub"}
COURSE_REGEX = re.compile(r"(CS-\d{3})", re.IGNORECASE)


def load_meta():
    meta = {}
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            for line in f:
                fname, ts = line.strip().split("|")
                meta[fname] = float(ts)
    return meta


def save_meta(meta):
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


def generate_file_blocks(files, is_notes=False):
    """Return HTML blocks for assignments or notes"""
    blocks = []
    for f in sorted(files):
        name = os.path.splitext(os.path.basename(f))[0]
        keywords = name.replace("_", " ").lower()

        if is_notes:
            block = f"""
          <li class="fileRow" data-keywords="{keywords}">
            <div class="left"><img class="icon" src="https://img.icons8.com/color/48/000000/book.png" alt="Book icon"/>{name}</div>
            <div>
              <a href="{f}" target="_blank" class="download-link" aria-label="Download {name}">Download</a>
              <span class="file-size">({file_size(f)})</span>
              <div class="epub-msg">Use Moon+ Reader or any EPUB reader app.</div>
            </div>
          </li>"""
        else:
            block = f"""
        <div class="pdf-block fileRow" data-keywords="{keywords}">
          <div class="pdf-title"><img class="icon" src="https://img.icons8.com/color/48/000000/pdf.png" alt="PDF icon"/>{name}</div>
          <iframe class="pdf-frame" src="{f}" aria-label="View {name}"></iframe><br>
          <a href="{f}" target="_blank" class="download-link" aria-label="Download {name}">Download PDF</a>
          <span class="file-size">({file_size(f)})</span>
        </div>"""
        blocks.append(block)
    return "\n".join(blocks)


def main():
    files = [f for f in os.listdir(ROOT) if os.path.isfile(f)]
    meta = load_meta()
    now = datetime.datetime.now().timestamp()
    new_files = []

    assignments = []
    notes = []

    for f in sorted(files):
        ext = os.path.splitext(f)[1].lower()
        if ext in ALLOWED_ASSIGN_EXT:
            assignments.append(f)
        elif ext in ALLOWED_NOTES_EXT:
            notes.append(f)

        # track new
        mtime = os.path.getmtime(f)
        if f not in meta or meta[f] < mtime:
            meta[f] = mtime
        if now - meta[f] <= 3 * 86400:
            new_files.append(f)

    save_meta(meta)

    # banner
    banner_html = ""
    if new_files:
        links = " — ".join([f'<a href="{f}">{f}</a>' for f in new_files])
        banner_html = f'<div class="new-banner">🆕 New files added: {links}</div>'

    # build page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSE • Notes & Assignments</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/1f4da.png" />
  <style>
    body {{ background: #181e26; color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; min-height: 100vh; text-align: center; transition: background .3s, color .3s;}}
    .lightmode {{ background: #f6f7f9; color: #232333;}}
    .darkmode-btn {{ position:fixed;top:13px;right:13px;padding:6px 14px;font-size:1em;background:#253168;color:#f6f7f9;border:none;border-radius:20px;cursor:pointer;z-index:10; transition:.2s; box-shadow:0 1px 5px #0001;}}
    h1 {{ font-size:2.11rem;margin:30px 0 6px 0;}}
    .desc {{ color:#b5bac2; margin-bottom:4px; font-size:1.01em;}}
    .update-bar {{background:#21396c; color:#e3ecfd; margin:20px auto 18px; padding:7px 22px; font-size:.99em; border-radius:13px; max-width:570px;}}
        .new-banner {
      background: #243b66;
      color: #e6f1ff;
      margin: 20px auto 14px;
      padding: 9px 16px;
      border-radius: 10px;
      max-width: 640px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.35);
      font-size: 0.97em;
    }
    .new-banner a {
      color: #63b3ff;
      text-decoration: none;
      font-weight: 500;
    }
    .new-banner a:hover {
      text-decoration: underline;
      color: #8fd0ff;
    }
    main {{ max-width:700px;padding:0 8px;margin: 0 auto; }}
    .search-box {{margin:15px 0;}}
    .search-input{{padding:9px 14px;font-size:1.04em;width:72%;max-width:285px;border-radius:6px;border:1px solid #374b63;background:#21293b;color:#f6f7f9;}}
    .last-updated{{margin:4px auto 18px;font-size:.94em;color:#8dacbe;}}
    .collapse-btn {{ margin:0 auto 3px;display:block;padding:7px 20px;font-size:1.01em;background:#183478;color:#dbe7fa;border:none;border-radius:9px;cursor:pointer;transition:.2s;}}
    section {{margin:32px 0 16px 0;}}
    .section-title {{margin-bottom:11px;font-size:1.11rem;text-transform:uppercase;letter-spacing:.7px;}}
    .pdf-block {{margin:26px 0;background:#232b36;border-radius:13px;padding:18px 10px 13px;box-shadow:0 2.5px 9px #0003;}}
    .pdf-title {{font-size:1.08em; margin-bottom:10px; display:flex;align-items:center;justify-content:center;}}
    .pdf-title .icon {{width:19px;height:19px;margin-right:8px;}}
    .pdf-frame {{width:99%;max-width:660px;height:340px;border:1.5px solid #313141;border-radius:8px;background:#111015;margin-bottom:10px;}}
    .download-link {{display:inline-block; background:#203048;color:#8adcff;text-decoration:none;font-weight:500;font-size:1em; border-radius:8px;padding:6px 19px;transition:background .15s;box-shadow:0 1px 3.5px #0bf2;}}
    .download-link:hover {{background:#1e2a39;color:#b7f3ff;}}
    .file-size {{font-size:.95em;color:#bbe1d7;margin-left:9px;}}
    .file-list {{list-style:none;padding:0;margin:13px 0;}}
    .file-list li {{ margin:9px 0; padding:9px 8px; background:#232b36; border-radius:9px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;box-shadow:0 1.5px 7px #0001;}}
    .file-list .left {{display:flex;align-items:center;}}
    .file-list .icon {{width:18px;height:18px;margin-right:7px;}}
    .epub-msg {{font-size:.9em;color:#aef1bb;margin-top:2px;}}
    .footer {{margin:38px 0 14px 0;opacity:.61;font-size:.97em;}}
    .feedback {{background:#21396c;color:#e8f2fa;font-size:.98em;padding:7px 16px;border-radius:7px;display:inline-block;margin-top:10px;text-decoration:none;}}
    .qr-section {{margin: 23px 0;}}
    .qr-img {{width:108px;display:block;margin:7px auto;}}
    @media (max-width:700px) {{
      .pdf-frame {{height:39vw;min-height:150px;}}
      .file-list li {{flex-direction: column;align-items:flex-start;}}
      .file-list .left {{margin-bottom:7px;}}
    }}
  </style>
</head>
<body>
  <button class="darkmode-btn" id="modeBtn" aria-label="Toggle Dark/Light Mode">🌙</button>
  <h1 title="Assignments & Notes Repository">CSE Notes & Assignments</h1>
  <div class="desc">Instant download and reading for CSE students. All Assignment and Notes for you guys 😉!</div>
  {banner_html}
  <div class="update-bar" id="update-bar">📢 Latest updates <span id="today"></span></div>
  <div class="last-updated">Last updated: <span id="lastUpdate"></span></div>
  <main>
    <div class="search-box">
      <input class="search-input" type="text" placeholder="Type to filter assignments/notes..." oninput="filterFiles()" id="searchBox" aria-label="Filter files">
    </div>
    <section>
      <button class="collapse-btn" type="button" onclick="toggleSection('assignmentsSection')">Assignments (PDF) ⬇️</button>
      <div id="assignmentsSection">
        {generate_file_blocks(assignments, is_notes=False)}
      </div>
    </section>
    <section>
      <button class="collapse-btn" type="button" onclick="toggleSection('notesSection')">Notes (EPUB) ⬇️</button>
      <div id="notesSection">
        <ul class="file-list">
          {generate_file_blocks(notes, is_notes=True)}
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
    <div class="footer">
        &copy; Aryan Singh Chandel | CSE Section-A, 2025
    </div>
  </main>
  <script>
    function toggleSection(sectionId) {{
      var s = document.getElementById(sectionId);
      if (s.style.display === "none") s.style.display = "block";
      else s.style.display = "none";
    }}
    document.getElementById('assignmentsSection').style.display = "block";
    document.getElementById('notesSection').style.display = "block";
    let mode = localStorage.getItem("mode") || "dark";
    function setMode(m) {{
      if(m==="light") {{
        document.body.classList.add("lightmode");
        document.getElementById('modeBtn').textContent="🌞";
      }} else {{
        document.body.classList.remove("lightmode");
        document.getElementById('modeBtn').textContent="🌙";
      }}
      localStorage.setItem("mode", m);
    }}
    setMode(mode);
    document.getElementById('modeBtn').onclick = function() {{
      mode = (mode === "dark") ? "light" : "dark";
      setMode(mode);
    }};
    function filterFiles() {{
      let v = document.getElementById('searchBox').value.toLowerCase();
      document.querySelectorAll('.fileRow').forEach(function(row) {{
        let keys = row.getAttribute('data-keywords') || '';
        row.style.display = (keys.includes(v) || v === "") ? "" : "none";
      }});
    }}
    var update = new Date(document.lastModified);
    document.getElementById("lastUpdate").textContent = update.toLocaleDateString() + " " + update.toLocaleTimeString();
    document.getElementById("today").textContent = " (" + update.toLocaleDateString() + ")";
  </script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
          
