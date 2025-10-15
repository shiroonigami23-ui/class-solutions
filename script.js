document.addEventListener('DOMContentLoaded', function() {
    
    // --- Dark/Light Mode Toggle ---
    const modeBtn = document.getElementById('modeBtn');
    // Read the saved mode from localStorage, default to 'dark'
    let currentMode = localStorage.getItem("mode") || "dark";

    const setMode = (mode) => {
        if (mode === "light") {
            document.body.classList.add("lightmode");
            modeBtn.textContent = "🌞";
        } else {
            document.body.classList.remove("lightmode");
            modeBtn.textContent = "🌙";
        }
        localStorage.setItem("mode", mode);
    };

    // Set initial mode on page load
    setMode(currentMode);

    // Add click event listener to the button
    modeBtn.addEventListener('click', () => {
        currentMode = (currentMode === "dark") ? "light" : "dark";
        setMode(currentMode);
    });

    // --- Last Updated Timestamp ---
    const lastUpdateSpan = document.getElementById("lastUpdate");
    if (lastUpdateSpan) {
        // This date is automatically set by the python script during generation
        const update = new Date(); 
        lastUpdateSpan.textContent = update.toLocaleString();
    }
    
    // --- Hide "New Files" Banner if Empty ---
    const newFilesContent = document.getElementById('new-files-content');
    if (newFilesContent && newFilesContent.textContent.trim().includes('No new files')) {
        const newFilesBanner = document.getElementById('new-files-banner');
        if (newFilesBanner) {
            newFilesBanner.style.display = 'none';
        }
    }

});

// --- File Filtering Function ---
// This function is called directly from the oninput event in the HTML
function filterFiles() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    const fileRows = document.querySelectorAll('.file-row');

    fileRows.forEach(row => {
        const keywords = row.getAttribute('data-keywords') || '';
        const isVisible = keywords.toLowerCase().includes(searchTerm);
        row.style.display = isVisible ? '' : 'none';
    });
}
