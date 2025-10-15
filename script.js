document.addEventListener('DOMContentLoaded', function() {
    // --- Tab System ---
    const tabs = document.querySelectorAll('.tab-link');
    if (tabs.length > 0) {
        // Open the 'All Files' tab by default if it exists, otherwise the first tab
        const defaultTab = document.querySelector('.tab-link[onclick*="AllFiles"]') || tabs[0];
        defaultTab.click();
    }
});

function openTab(event, tabName) {
    // Hide all tab content panels
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    
    // Deactivate all tab link buttons
    document.querySelectorAll('.tab-link').forEach(link => link.classList.remove('active'));
    
    // Show the selected tab content and activate its link
    const activeTab = document.getElementById(tabName);
    if(activeTab) {
        activeTab.style.display = 'block';
    }
    event.currentTarget.classList.add('active');
}

// --- File Filtering ---
function filterFiles() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    document.querySelectorAll('.file-row').forEach(row => {
        const keywords = row.getAttribute('data-keywords') || '';
        // A file is shown if its keywords include the search term
        const isMatch = keywords.toLowerCase().includes(searchTerm);
        row.style.display = isMatch ? '' : 'none'; // Use empty string to reset to default display
    });
}
