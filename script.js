document.addEventListener('DOMContentLoaded', function () {
    const searchBox = document.getElementById('searchBox');
    const semesterButtons = document.querySelectorAll('.semester-option');
    const tabButtons = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    let selectedSemester = localStorage.getItem('selectedSemester') || 'all';

    function applyFilters() {
        const searchTerm = (searchBox?.value || '').toLowerCase();

        document.querySelectorAll('.file-row').forEach((row) => {
            const keywords = (row.getAttribute('data-keywords') || '').toLowerCase();
            const semester = row.getAttribute('data-semester') || '';

            const matchesSearch = keywords.includes(searchTerm);
            const matchesSemester = selectedSemester === 'all' || semester === selectedSemester;

            row.style.display = matchesSearch && matchesSemester ? '' : 'none';
        });

        const activeTab = document.querySelector('.tab-content[style*="block"]') || document.querySelector('.tab-content');
        let visibleInTab = 0;
        if (activeTab) {
            activeTab.querySelectorAll('.file-row').forEach(function (row) {
                if (row.style.display !== 'none') visibleInTab++;
            });
        }
        const noResultsEl = document.getElementById('no-results-message');
        if (noResultsEl) noResultsEl.classList.toggle('hidden', visibleInTab > 0);
    }

    function setSemester(value) {
        selectedSemester = value;
        localStorage.setItem('selectedSemester', value);

        semesterButtons.forEach((button) => {
            button.classList.toggle('active', button.dataset.semester === value);
        });

        applyFilters();
    }

    function openTab(tabId) {
        tabContents.forEach((tab) => {
            tab.style.display = tab.id === tabId ? 'block' : 'none';
        });

        tabButtons.forEach((button) => {
            button.classList.toggle('active', button.dataset.tab === tabId);
        });

        applyFilters();
    }

    semesterButtons.forEach((button) => {
        button.addEventListener('click', function () {
            setSemester(button.dataset.semester || 'all');
        });
    });

    tabButtons.forEach((button) => {
        button.addEventListener('click', function () {
            openTab(button.dataset.tab);
        });
    });

    if (searchBox) {
        searchBox.addEventListener('input', applyFilters);
    }

    if (!Array.from(semesterButtons).some((button) => button.dataset.semester === selectedSemester)) {
        selectedSemester = 'all';
    }

    const initialTab = tabButtons[0]?.dataset.tab;
    if (initialTab) {
        openTab(initialTab);
    }
    setSemester(selectedSemester);
});
