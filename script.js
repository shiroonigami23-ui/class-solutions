document.addEventListener('DOMContentLoaded', function () {
    const searchBox = document.getElementById('searchBox');
    const semesterButtons = document.querySelectorAll('.semester-option');
    const tabButtons = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    const courseFilter = document.getElementById('courseFilter');
    const typeFilter = document.getElementById('typeFilter');
    const sortFilter = document.getElementById('sortFilter');

    let selectedSemester = localStorage.getItem('selectedSemester') || 'all';

    function cardVisible(row, searchTerm) {
        const keywords = (row.getAttribute('data-keywords') || '').toLowerCase();
        const semester = row.getAttribute('data-semester') || '';
        const course = row.getAttribute('data-course') || '';
        const type = row.getAttribute('data-type') || '';

        const matchesSearch = keywords.includes(searchTerm);
        const matchesSemester = selectedSemester === 'all' || semester === selectedSemester;
        const matchesCourse = !courseFilter || courseFilter.value === 'all' || course === courseFilter.value;
        const matchesType = !typeFilter || typeFilter.value === 'all' || type === typeFilter.value;
        return matchesSearch && matchesSemester && matchesCourse && matchesType;
    }

    function applySort(activeTab) {
        if (!sortFilter || !activeTab) return;
        const grid = activeTab.querySelector('.file-grid');
        if (!grid) return;
        const cards = Array.from(grid.querySelectorAll('.file-row'));
        cards.sort((a, b) => {
            const mode = sortFilter.value;
            if (mode === 'name') {
                const an = (a.querySelector('.file-title')?.textContent || '').toLowerCase();
                const bn = (b.querySelector('.file-title')?.textContent || '').toLowerCase();
                return an.localeCompare(bn);
            }
            const ad = Date.parse(a.getAttribute('data-date') || 0);
            const bd = Date.parse(b.getAttribute('data-date') || 0);
            return mode === 'oldest' ? ad - bd : bd - ad;
        });
        cards.forEach((card) => grid.appendChild(card));
    }

    function applyFilters() {
        const searchTerm = (searchBox?.value || '').toLowerCase().trim();
        document.querySelectorAll('.file-row').forEach((row) => {
            row.style.display = cardVisible(row, searchTerm) ? '' : 'none';
        });

        const activeTab = document.querySelector('.tab-content[style*="block"]') || document.querySelector('.tab-content');
        applySort(activeTab);

        let visibleInTab = 0;
        if (activeTab) {
            activeTab.querySelectorAll('.file-row').forEach((row) => {
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
    [searchBox, courseFilter, typeFilter, sortFilter].forEach((el) => {
        if (el) el.addEventListener('input', applyFilters);
        if (el) el.addEventListener('change', applyFilters);
    });

    if (!Array.from(semesterButtons).some((button) => button.dataset.semester === selectedSemester)) {
        selectedSemester = 'all';
    }
    const initialTab = tabButtons[0]?.dataset.tab;
    if (initialTab) openTab(initialTab);
    setSemester(selectedSemester);
});
