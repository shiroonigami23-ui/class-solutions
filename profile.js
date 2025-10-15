document.addEventListener('DOMContentLoaded', function() {
    
    // --- Modal Elements ---
    const profileModal = document.getElementById('profileModal');
    const openModalBtn = document.getElementById('profile-pic');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // --- Profile Data Elements ---
    const nameInput = document.getElementById('profile-name-input');
    const nameDisplay = document.getElementById('modal-profile-name');
    const headerPic = document.getElementById('profile-pic');
    const modalPic = document.getElementById('modal-profile-pic');
    const picUpload = document.getElementById('modal-pic-upload');
    const saveBtn = document.getElementById('save-profile-btn');
    
    // --- Open/Close Modal ---
    openModalBtn.addEventListener('click', () => profileModal.classList.add('active'));
    closeModalBtn.addEventListener('click', () => profileModal.classList.remove('active'));
    profileModal.addEventListener('click', (e) => {
        if (e.target === profileModal) {
            profileModal.classList.remove('active');
        }
    });

    // --- Profile Personalization ---
    const loadProfileData = () => {
        const savedName = localStorage.getItem('userName') || 'Your Name';
        const savedPic = localStorage.getItem('userPic');
        
        nameInput.value = savedName === 'Your Name' ? '' : savedName;
        nameDisplay.textContent = savedName;

        if (savedPic) {
            headerPic.src = savedPic;
            modalPic.src = savedPic;
        }
    };

    // Save Profile Data
    saveBtn.addEventListener('click', () => {
        const newName = nameInput.value.trim();
        if (newName) {
            localStorage.setItem('userName', newName);
            nameDisplay.textContent = newName;
        } else {
            localStorage.removeItem('userName');
            nameDisplay.textContent = 'Your Name';
        }
        alert('Profile saved successfully!');
        profileModal.classList.remove('active');
    });

    // Handle Picture Upload
    picUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const imageUrl = e.target.result;
                localStorage.setItem('userPic', imageUrl);
                headerPic.src = imageUrl;
                modalPic.src = imageUrl;
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
    
    modeBtn.addEventListener('click', () => {
        currentMode = (currentMode === "dark") ? "light" : "dark";
        setMode(currentMode);
    });

    // Initial load
    loadProfileData();
    setMode(currentMode);
});

// --- NEW Function for Modal Tabs ---
function openProfileTab(evt, tabName) {
    // Get all elements with class="modal-tab-content" and hide them
    const tabcontent = document.getElementsByClassName("modal-tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="modal-tab-link" and remove the class "active"
    const tablinks = document.getElementsByClassName("modal-tab-link");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
