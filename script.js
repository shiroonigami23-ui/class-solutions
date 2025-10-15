document.addEventListener('DOMContentLoaded', function() {
    
    // --- Profile Dropdown Logic ---
    const profileArea = document.querySelector('.profile-area');
    const profilePic = document.getElementById('profile-pic');
    profilePic.addEventListener('click', () => profileArea.classList.toggle('active'));
    document.addEventListener('click', (e) => {
        if (!profileArea.contains(e.target)) {
            profileArea.classList.remove('active');
        }
    });

    // --- Profile Personalization ---
    const nameInput = document.getElementById('profile-name-input');
    const nameDisplay = document.getElementById('profile-name-display');
    const saveBtn = document.getElementById('save-profile-btn');
    const picUpload = document.getElementById('profile-pic-upload');
    const dropdownPic = document.getElementById('dropdown-profile-pic');

    // Load saved data from localStorage
    const savedName = localStorage.getItem('userName');
    const savedPic = localStorage.getItem('userPic');

    if (savedName) {
        nameDisplay.textContent = savedName;
        nameInput.value = savedName;
    }
    if (savedPic) {
        profilePic.src = savedPic;
        dropdownPic.src = savedPic;
    }

    // Save Name
    saveBtn.addEventListener('click', () => {
        const newName = nameInput.value.trim();
        if (newName) {
            localStorage.setItem('userName', newName);
            nameDisplay.textContent = newName;
            alert('Profile saved!');
            profileArea.classList.remove('active');
        }
    });

    // Handle Picture Upload
    picUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const imageUrl = e.target.result;
                localStorage.setItem('userPic', imageUrl);
                profilePic.src = imageUrl;
                dropdownPic.src = imageUrl;
            }
            reader.readAsDataURL(file);
        }
    });

    // --- Dark/Light Mode Toggle ---
    const modeBtn = document.getElementById('modeBtn');
    let currentMode = localStorage.getItem("themeMode") || "dark";

    const setMode = (mode) => {
        if (mode === "light") {
            document.body.classList.add("lightmode");
            modeBtn.textContent = "🌙";
        } else {
            document.body.classList.remove("lightmode");
            modeBtn.textContent = "☀️";
        }
        localStorage.setItem("themeMode", mode);
    };
    setMode(currentMode);
    modeBtn.addEventListener('click', () => {
        currentMode = (currentMode === "dark") ? "light" : "dark";
        setMode(currentMode);
    });

    // --- Tab System ---
    const tabs = document.querySelectorAll('.tab-link');
    if (tabs.length > 0) {
        // Open the 'All Files' tab by default if it exists, otherwise the first tab
        const defaultTab = document.querySelector('.tab-link[onclick*="AllFiles"]') || tabs[0];
        defaultTab.click();
    }
});

function openTab(event, tabName) {
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    // Deactivate all tab links
    document.querySelectorAll('.tab-link').forEach(link => link.classList.remove('active'));
    // Show the selected tab content and activate its link
    document.getElementById(tabName).style.display = 'block';
    event.currentTarget.classList.add('active');
}

// --- File Filtering ---
function filterFiles() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    document.querySelectorAll('.file-row').forEach(row => {
        const keywords = row.getAttribute('data-keywords') || '';
        row.style.display = keywords.toLowerCase().includes(searchTerm) ? '' : 'none';
    });
}
