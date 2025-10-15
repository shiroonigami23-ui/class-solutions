const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewArea = document.getElementById('preview-area');
const fileNamePreview = document.getElementById('file-name-preview');
const pdfCanvas = document.getElementById('pdf-preview-canvas');
const imagePreview = document.getElementById('image-preview');
const textPreview = document.getElementById('text-preview');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const shareLinkInput = document.getElementById('share-link-input');
const githubSubmitBtn = document.getElementById('github-submit-btn');

let selectedFile = null;

// --- Event Listeners ---
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        handleFilePreview(selectedFile);
    }
});
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragging');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        fileInput.files = e.dataTransfer.files; // Sync with file input
        handleFilePreview(selectedFile);
    }
});

shareLinkInput.addEventListener('input', () => {
    if (shareLinkInput.value.trim() !== '' && selectedFile) {
        step3.classList.remove('hidden');
        updateGitHubLink();
    } else {
        step3.classList.add('hidden');
    }
});

// --- Functions ---
function handleFilePreview(file) {
    // Reset previews
    pdfCanvas.style.display = 'none';
    imagePreview.style.display = 'none';
    textPreview.style.display = 'none';

    fileNamePreview.textContent = `File: ${file.name}`;
    previewArea.classList.remove('hidden');
    step2.classList.remove('hidden');

    const extension = file.name.split('.').pop().toLowerCase();

    if (extension === 'pdf') {
        renderPdf(file);
    } else if (['jpg', 'jpeg', 'png'].includes(extension)) {
        renderImage(file);
    } else if (['txt', 'md'].includes(extension)) {
        renderText(file);
    } else {
        fileNamePreview.textContent += " (Preview not available)";
    }
}

function renderPdf(file) {
    pdfCanvas.style.display = 'block';
    const fileReader = new FileReader();
    fileReader.onload = function() {
        const typedarray = new Uint8Array(this.result);
        pdfjsLib.getDocument(typedarray).promise.then(pdf => {
            return pdf.getPage(1);
        }).then(page => {
            const viewport = page.getViewport({ scale: 0.5 });
            const context = pdfCanvas.getContext('2d');
            pdfCanvas.height = viewport.height;
            pdfCanvas.width = viewport.width;
            page.render({ canvasContext: context, viewport: viewport });
        });
    };
    fileReader.readAsArrayBuffer(file);
}

function renderImage(file) {
    imagePreview.style.display = 'block';
    imagePreview.src = URL.createObjectURL(file);
}

function renderText(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        textPreview.style.display = 'block';
        textPreview.textContent = e.target.result.substring(0, 500) + '...'; // Show first 500 chars
    };
    reader.readAsText(file);
}

function updateGitHubLink() {
    const repoURL = "https://github.com/shiroonigami23-ui/class-solutions/issues/new";
    const title = `File Submission: ${selectedFile.name}`;
    const body = `**File Name:**\n${selectedFile.name}\n\n**Shareable Link:**\n${shareLinkInput.value.trim()}`;
    const issueURL = `${repoURL}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
    githubSubmitBtn.href = issueURL;
}
