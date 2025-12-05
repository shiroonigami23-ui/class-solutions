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

The repository currently hosts materials for:

| Code | Subject | Type of Content |
| :--- | :--- | :--- |
| **CS-501** | Theory of Computation (TOC) | Assignments, Notes (NFA/DFA), Graph Solutions |
| **CS-502** | DBMS | Unit Notes, Assignment Solutions |
| **CS-503** | Cyber Security & Data Analytics | Assignments, Digital Notes, EPUBs |
| **CS-504** | Internet & Web Tech | Web Development Assignments, Notes |

---

## 🎮 How to Use

1. **Visit the Site:** Open the [Live Link](https://shiroonigami23-ui.github.io/class-solutions/).
2. **Find a File:**
   - Use the **Search Bar** at the top.
   - Or click the **Tags** (e.g., "Notes", "Documents") to filter.
3. **Preview/Download:**
   - Click **Preview** to read the file in a modal.
   - Click **View/Download** to save it to your device.
4. **Contribute:** Click on your profile icon to access the contribution page or settings.

---

## 🤝 How to Contribute

We welcome new notes and assignments! To add your files:

### Option 1: Via GitHub (Recommended)
1. **Fork** this repository.
2. Upload your file to the `files/` directory.
3. Open `data.json` (or the relevant data file) and add an entry for your new file following the existing format:
   ```json
   {
     "name": "Your File Name",
     "subject": "CS-XXX",
     "type": "pdf",
     "size": "1.2 MB",
     "link": "files/yourfile.pdf"
   }
   
