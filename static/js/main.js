(function () {
    'use strict';

    // ─── الوضع الغامق ───
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'light';

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : '');
        if (themeToggle) {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    applyTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = localStorage.getItem('theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', next);
            applyTheme(next);
        });
    }

    // ─── القائمة الجانبية على الموبايل ───
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    }

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // ─── فلاتر تلقائية ───
    document.querySelectorAll('.filter-auto').forEach(function (el) {
        el.addEventListener('change', function () {
            const form = el.closest('form');
            if (form) form.submit();
        });
    });

    // فلاتر في شريط الفلاتر (select بدون class filter-auto)
    document.querySelectorAll('.filters-form select').forEach(function (el) {
        el.addEventListener('change', function () {
            const form = el.closest('form');
            if (form) form.submit();
        });
    });
})();
