document.addEventListener('DOMContentLoaded', function() {
    
    // --- Modal Elements ---
    const profileModal = document.getElementById('profileModal');
    const openModalBtn = document.getElementById('profile-pic');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // --- Profile Data Elements ---
    const nameInput = document.getElementById('profile-name-input');
    const githubUserInput = document.getElementById('github-username-input');
    const nameDisplay = document.getElementById('modal-profile-name');
    const headerPic = document.getElementById('profile-pic');
    const modalPicWrapper = document.querySelector('.modal-profile-pic-wrapper');
    const modalPic = document.getElementById('modal-profile-pic');
    const picUploadInput = document.getElementById('modal-pic-upload');
    const saveBtn = document.getElementById('save-profile-btn');
    const contributionsList = document.getElementById('user-contributions-list');

    // --- Open/Close Modal ---
    openModalBtn.addEventListener('click', () => {
        loadProfileData(); // Load data every time modal is opened
        displayUserContributions();
        profileModal.classList.add('active');
    });
    closeModalBtn.addEventListener('click', () => profileModal.classList.remove('active'));
    profileModal.addEventListener('click', (e) => {
        if (e.target === profileModal) {
            profileModal.classList.remove('active');
        }
    });

    // --- Profile Personalization ---
    const loadProfileData = () => {
        const savedName = localStorage.getItem('userName') || 'Your Name';
        const savedGithubUser = localStorage.getItem('githubUsername') || '';
        const savedPic = localStorage.getItem('userPic');
        
        nameInput.value = savedName === 'Your Name' ? '' : savedName;
        githubUserInput.value = savedGithubUser;
        nameDisplay.textContent = savedName;

        if (savedPic) {
            headerPic.src = savedPic;
            modalPic.src = savedPic;
        }
    };

    saveBtn.addEventListener('click', () => {
        const newName = nameInput.value.trim();
        const newGithubUser = githubUserInput.value.trim();

        if (newName) {
            localStorage.setItem('userName', newName);
            nameDisplay.textContent = newName;
        } else {
            localStorage.removeItem('userName');
            nameDisplay.textContent = 'Your Name';
        }
        
        if (newGithubUser) {
            localStorage.setItem('githubUsername', newGithubUser);
        } else {
            localStorage.removeItem('githubUsername');
        }

        alert('Profile saved successfully!');
        profileModal.classList.remove('active');
    });

    // --- NEW Slick Image Upload ---
    modalPicWrapper.addEventListener('click', () => {
        picUploadInput.click();
    });

    picUploadInput.addEventListener('change', (event) => {
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

    // --- NEW Display User Contributions ---
    const displayUserContributions = () => {
        const githubUsername = localStorage.getItem('githubUsername');
        contributionsList.innerHTML = ''; // Clear previous list

        if (!githubUsername) {
            contributionsList.innerHTML = '<p class="contributions-empty-state">Set your GitHub username in Settings to see your contributions!</p>';
            return;
        }

        const userFiles = Object.entries(window.contributorsData)
            .filter(([filename, contributor]) => contributor.toLowerCase() === githubUsername.toLowerCase())
            .map(([filename]) => filename);

        if (userFiles.length === 0) {
            contributionsList.innerHTML = '<p class="contributions-empty-state">You haven\'t contributed any files yet. Be the first!</p>';
        } else {
            userFiles.forEach(filename => {
                const li = document.createElement('li');
                li.textContent = filename.replace(/_/g, ' ');
                contributionsList.appendChild(li);
            });
        }
    };

    // --- Dark/Light Mode Toggle ---
    const modeBtn = document.getElementById('modeBtn');
    let currentMode = localStorage.getItem("themeMode") || "dark";
    const setMode = (mode) => {
        document.body.classList.toggle("lightmode", mode === "light");
        modeBtn.textContent = mode === "light" ? "🌙" : "☀️";
        localStorage.setItem("themeMode", mode);
    };
    modeBtn.addEventListener('click', () => {
        currentMode = (currentMode === "dark") ? "light" : "dark";
        setMode(currentMode);
    });

    // Initial load for theme
    setMode(currentMode);
});

// --- Function for Modal Tabs ---
function openProfileTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("modal-tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    const tablinks = document.getElementsByClassName("modal-tab-link");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
         }
