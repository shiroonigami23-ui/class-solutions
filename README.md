# 📚 CSE Student Hub

![Status](https://img.shields.io/badge/Status-Live-success)
![Subject](https://img.shields.io/badge/Subject-Computer_Science-blue)
![Resources](https://img.shields.io/badge/Resources-Notes_&_Assignments-orange)

> **Your central dashboard for accessing engineering notes, assignments, and study resources.**

**CSE Student Hub** is a centralized repository designed to simplify file sharing for Computer Science students. It provides a clean, searchable interface to access lecture notes, assignment solutions, and reference materials for various subjects (CS-501, CS-502, etc.), eliminating the need to scroll through endless chat groups.

---

## 🔗 Access the Hub

**View and download resources instantly:**
### [🚀 Launch Student Hub](https://shiroonigami23-ui.github.io/class-solutions/)

---

## ✨ Key Features

### 📂 Organized Resource Library
- **Subject Categorization:** Files are tagged by subject codes (e.g., `CS-501` for TOC, `CS-502` for DBMS) for easy navigation.
- **Smart Filtering:** Filter content by type:
  - 📄 **Documents:** PDFs of assignments and reports.
  - 📝 **Notes:** Hand-written or digital notes (PDF/EPUB).
  - 🖼️ **Images:** Diagrams and snapshots.

### 🔍 Search & Preview
- **Instant Search:** Quickly find specific files by name (e.g., "Cyber Security", "Assignment 2").
- **Live Preview:** View PDFs and images directly in the browser without downloading them first.

### 👤 User Dashboard & Contributions
- **Personalized Profile:** Set your display name and GitHub username.
- **Theme Support:** Switch between Light and Dark modes.
- **Contribution System:** Users can upload their own notes or assignments to help the community (via Pull Request or Form).

### 📱 Mobile Friendly
- **Responsive Design:** Optimized for phones and tablets.
- **QR Code Sharing:** Built-in QR generator to instantly share the site with classmates.

---

## 📖 Available Subjects

The hub supports **5th and 6th semester** subjects. Choose your semester on the site to filter files.

| Code | Subject | Semester |
| :--- | :--- | :--- |
| **CS-501** | Theory of Computation (TOC) | 5 |
| **CS-502** | DBMS | 5 |
| **CS-503** | Cyber Security & Data Analytics | 5 |
| **CS-504** | Internet & Web Tech | 5 |
| **CS-601** | Machine Learning | 6 |
| **CS-602** | Computer Network | 6 |
| **CS-603** | Compiler/Graphics | 6 |
| **CS-604** | Project Management | 6 |
| **CS-605** | Data Analytics Lab | 6 |
| **CS-606** | Skill Development Lab | 6 |

---

## 🎮 How to Use

1. **Visit the Site:** Open the [Live Link](https://shiroonigami23-ui.github.io/class-solutions/).
2. **Choose your semester** (Step 1) — e.g. Semester 5 or 6 — to see relevant files.
3. **Find a File:**
   - Use the **Search bar** to filter by name, course code, or keyword.
   - Use the **tabs** (All Files, Documents, Images, Notes) to filter by type.
4. **Preview/Download:**
   - Click **Preview** for PDFs in-browser.
   - Click **View** to open or download the file.
5. **Contribute:** Click your profile icon for settings and the contribution page.

---

## 🤝 How to Contribute

We welcome new notes and assignments! Use the **semester workflow** below (drop files in repo root and run the generator). You can also use the in-app contribution form (profile → Contribute a New File).

---

## Semester Workflow (5th & 6th sem)

**Same automatic flow for all semesters:**

1. **Drop files** into the repository root (PDFs, EPUBs, images, etc.).
2. **Run once:** `python generate_index.py`
3. The script scans the root, assigns each file to a subject and semester from `subjects.yaml`, and regenerates `index.html`.

**No need to edit `subjects.yaml`** unless you add a **new** subject code. Existing 5th and 6th sem subjects (CS-501–CS-504, CS-601–CS-606) are already configured.

### How files get assigned (6th sem and others)

The script matches **filenames** to courses using **keywords** in `subjects.yaml`. It is flexible with naming:

- **Course code in name:** `CS601_Notes.pdf`, `CS-601-ML.pdf`, `601_Assignment.pdf` → **CS-601** (Machine Learning)
- **Subject words:** `Machine_Learning_Unit1.pdf`, `Computer_Network_notes.pdf` → **CS-601**, **CS-602**
- **Spaces/hyphens/underscores** in filenames are ignored for matching, so `CS-601` and `CS601` both match.

6th sem courses (CS-601 to CS-606) have extra keywords so many name variants map to the correct 600-series. If a file still lands in “Uncategorized”, add a one-off mapping under `file_overrides` in `subjects.yaml` or rename the file to include the subject code or name.
