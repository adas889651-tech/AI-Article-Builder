/* main.js — global UI: dark mode, sidebar toggle, flash dismiss */

(function () {
  'use strict';

  // ── Dark mode ─────────────────────────────────────────────
  const html        = document.documentElement;
  const darkToggle  = document.getElementById('darkToggle');
  const DARK_KEY    = 'aab_theme';

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem(DARK_KEY, theme);
  }

  // Restore saved preference
  const saved = localStorage.getItem(DARK_KEY) || 'light';
  applyTheme(saved);

  if (darkToggle) {
    darkToggle.addEventListener('click', function () {
      const current = html.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // ── Sidebar mobile toggle ─────────────────────────────────
  const sidebar    = document.getElementById('sidebar');
  const menuToggle = document.getElementById('menuToggle');

  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 &&
          sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== menuToggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss flash messages after 4 s ─────────────────
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity    = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

})();
