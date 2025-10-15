document.addEventListener('DOMContentLoaded', () => {
    const previewModal = document.getElementById('pdfPreviewModal');
    const closeModalBtn = document.getElementById('closePdfModalBtn');
    const pdfCanvas = document.getElementById('pdf-canvas');
    const pdfTitle = document.getElementById('pdf-modal-title');
    const loader = document.getElementById('loader');
    const pdfjsLib = window['pdfjs-dist/build/pdf'];
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js`;

    let currentPdf = null;

    // Use event delegation to handle clicks on dynamically added buttons
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('preview-button')) {
            const pdfUrl = e.target.dataset.pdfUrl;
            openPdfPreview(pdfUrl);
        }
    });

    const openPdfPreview = (url) => {
        pdfTitle.textContent = "Loading...";
        loader.style.display = 'block';
        pdfCanvas.style.display = 'none';
        previewModal.classList.add('active');
        
        // Format title
        let formattedTitle = url.split('/').pop().replace(/_/g, ' ').replace('.pdf', '');
        pdfTitle.textContent = formattedTitle;

        // Load PDF
        pdfjsLib.getDocument(url).promise.then(pdf => {
            currentPdf = pdf;
            return pdf.getPage(1);
        }).then(page => {
            loader.style.display = 'none';
            pdfCanvas.style.display = 'block';
            const viewport = page.getViewport({ scale: 1.5 });
            const context = pdfCanvas.getContext('2d');
            pdfCanvas.height = viewport.height;
            pdfCanvas.width = viewport.width;
            page.render({ canvasContext: context, viewport: viewport });
        }).catch(error => {
            console.error('Error loading PDF:', error);
            pdfTitle.textContent = "Failed to load preview";
            loader.style.display = 'none';
        });
    };
    
    const closePreview = () => {
        previewModal.classList.remove('active');
        // Destroy the PDF object to free up memory
        if (currentPdf) {
            currentPdf.destroy();
            currentPdf = null;
        }
    };

    closeModalBtn.addEventListener('click', closePreview);
    previewModal.addEventListener('click', (e) => {
        if (e.target === previewModal) {
            closePreview();
        }
    });
});
