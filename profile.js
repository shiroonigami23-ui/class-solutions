document.addEventListener('DOMContentLoaded', function() {
    
    // --- Modal Elements ---
    const profileModal = document.getElementById('profileModal');
    const openModalBtn = document.getElementById('profile-pic');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // --- Profile Data Elements ---
    const nameInput = document.getElementById('profile-name-input');
    const headerPic = document.getElementById('profile-pic');
    const modalPic = document.getElementById('modal-profile-pic');
    const picUpload = document.getElementById('modal-pic-upload');
    const saveBtn = document.getElementById('save-profile-btn');
    
    // --- Open/Close Modal ---
    openModalBtn.addEventListener('click', () => profileModal.classList.add('active'));
    closeModalBtn.addEventListener('click', () => profileModal.classList.remove('active'));
    // Close modal if user clicks on the overlay
    profileModal.addEventListener('click', (e) => {
        if (e.target === profileModal) {
            profileModal.classList.remove('active');
        }
    });

    // --- Profile Personalization ---
    const loadProfileData = () => {
        const savedName = localStorage.getItem('userName');
        const savedPic = localStorage.getItem('userPic');
        if (savedName) {
            nameInput.value = savedName;
        }
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
