import os
import re

HTML_FILE = "index.html"

def get_existing_entries(html_content):
    """Find already listed file names in index.html to avoid duplicates."""
    pattern = r'href="([^"]+\.(?:pdf|epub))"'
    return set(re.findall(pattern, html_content, flags=re.IGNORECASE))

def generate_entry(filename):
    """Return HTML list item for a new file based on extension."""
    name = os.path.splitext(filename)[0]
    file_id = re.sub(r'[^a-zA-Z0-9]', '-', name.lower())  # safe ID

    if filename.lower().endswith(".pdf"):
        icon = "https://img.icons8.com/color/48/000000/pdf.png"
    else:
        icon = "https://img.icons8.com/color/48/000000/book.png"

    entry = f"""
<li class="fileRow" data-keywords="{name.lower()}">
  <div class="left">
    <img class="icon" src="{icon}" alt="file icon"/>{name}
  </div>
  <div>
    <a href="{filename}" target="_blank" class="download-link" aria-label="Download {name}">Download</a>
    <span class="file-size" id="size-{file_id}"></span>
  </div>
</li>
"""
    return entry, f'setSize("size-{file_id}", "{filename}");'

def main():
    if not os.path.exists(HTML_FILE):
        print("⚠️ index.html not found. Run inside repo root.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    existing_files = get_existing_entries(html_content)

    # Find all .pdf and .epub in repo root
    repo_files = [f for f in os.listdir(".") if f.lower().endswith((".pdf", ".epub"))]

    new_entries = []
    new_sizes = []

    for file in repo_files:
        if file not in existing_files:
            entry, size_call = generate_entry(file)
            new_entries.append(entry)
            new_sizes.append(size_call)

    if not new_entries:
        print("✅ No new files found, index.html unchanged.")
        return

    # Insert new <li> before closing </ul>
    updated_html = re.sub(
        r"(</ul>)",
        "\n".join(new_entries) + r"\n\1",
        html_content,
        count=1
    )

    # Insert new setSize calls before closing </script>
    updated_html = re.sub(
        r"(</script>)",
        "\n" + "\n".join(new_sizes) + r"\n\1",
        updated_html,
        count=1
    )

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"✨ Added {len(new_entries)} new entries to index.html")


if __name__ == "__main__":
    main()
    
