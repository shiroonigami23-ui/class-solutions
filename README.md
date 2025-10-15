CSE Student Hub - An Automated File Portal
Welcome to the CSE Student Hub, a self-updating, dynamic web portal designed to organize and display academic resources like notes, assignments, and documents for Computer Science & Engineering students.
[Live Demo Link Here] (Replace this with your actual GitHub Pages URL)
Key Features
Fully Automated Indexing: Simply push a new file to the repository, and the website automatically adds it to the list. No manual index.html editing is required.
Smart Categorization: Files are automatically sorted by course code (e.g., CS-501, CS-502) and by file type (Documents, Notes, Images) into a clean, tabbed interface.
User Personalization: Visitors can set their name and upload a custom profile picture, which is saved in their browser for a personalized experience.
Modern UI/UX: A clean, responsive design with a cheerful color scheme, complete with a dark/light mode toggle.
Instant Search: A live search bar allows users to filter through all the files in real-time.
Profile Page: A dedicated, full-page modal for a professional user settings experience.
The Core Logic: How It Works
The magic of this project lies in the synergy between a Python script and GitHub Actions. This combination creates a completely automated content management system.
1. The Trigger: git push & GitHub Actions
Every time you git push a new commit to your repository, a pre-configured GitHub Actions workflow is automatically triggered.
This workflow sets up a virtual environment, checks out your code, and runs the main Python script (generate_index.py).
2. The Engine: generate_index.py
This Python script is the heart of the operation. When it runs, it performs the following steps:
Scan & Collect: It scans the root directory of the repository for all files with supported extensions (.pdf, .epub, .jpg, etc.) while ignoring the core website files (like index.html, style.css, etc.).
Intelligent Categorization: For each file found, it:
Determines the Course Code by matching keywords in the filename (e.g., a file named TOC_Assignment_1.pdf contains "TOC", so it's assigned to CS-501).
Determines the File Type based on its extension (e.g., .pdf is a 'Document', .epub is 'Notes').
Generate HTML Snippets: It creates a clean, human-readable title from the filename and builds the HTML "card" for each file, embedding the title, course code, file size, and the correct icon.
Build the Page: It takes a master HTML template, injects all the generated file cards into the appropriate category tabs, and saves the final output as a brand new index.html file.
3. The Frontend: index.html, CSS, & JavaScript
The user-facing website is built with three main parts:
index.html: The main structure of the site. This file is completely overwritten by the Python script on every update.
style.css: Contains all the styling for the professional layout, the cheerful color theme, the responsive design, and the profile modal.
script.js & profile.js: These two files handle all the interactivity.
script.js: Manages the tab navigation system and the live search filter.
profile.js: Controls the pop-up profile modal, saves user data (name/avatar) to the browser's localStorage, and handles the theme toggle.
The final step in the workflow is committing the newly generated index.html back to the repository, making the update live on your GitHub Pages site.
How to Add New Files
Adding new content to the website is incredibly simple:
