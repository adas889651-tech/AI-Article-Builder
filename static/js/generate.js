/* generate.js — handles article generation, display, copy, PDF */

(function () {
  'use strict';

  const generateBtn   = document.getElementById('generateBtn');
  const loaderOverlay = document.getElementById('loaderOverlay');
  const loaderText    = document.getElementById('loaderText');
  const outputBody    = document.getElementById('outputBody');
  const outputToolbar = document.getElementById('outputToolbar');
  const copyBtn       = document.getElementById('copyBtn');
  const pdfBtn        = document.getElementById('pdfBtn');
  const editBtn       = document.getElementById('editBtn');

  // Cycling loader messages
  const loaderMsgs = [
    'Analysing your topic…',
    'Crafting SEO structure…',
    'Writing content…',
    'Polishing the article…',
    'Almost ready…',
  ];
  let loaderInterval = null;

  function startLoader() {
    let i = 0;
    loaderText.textContent = loaderMsgs[0];
    loaderOverlay.style.display = 'flex';
    loaderInterval = setInterval(function () {
      i = (i + 1) % loaderMsgs.length;
      loaderText.textContent = loaderMsgs[i];
    }, 1800);
  }

  function stopLoader() {
    clearInterval(loaderInterval);
    loaderOverlay.style.display = 'none';
  }

  // ── Generate ───────────────────────────────────────────────
  generateBtn.addEventListener('click', async function () {
    const title    = document.getElementById('art-title').value.trim();
    const keywords = document.getElementById('art-keywords').value.trim();
    const category = document.getElementById('art-category').value;
    const length   = document.querySelector('input[name="art-length"]:checked').value;
    const language = document.getElementById('art-language').value;

    if (!title) {
      alert('Please enter an article title.');
      document.getElementById('art-title').focus();
      return;
    }

    generateBtn.disabled = true;
    startLoader();
    outputToolbar.style.display = 'none';
    outputBody.innerHTML = '';

    try {
      const res = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, keywords, category, length, language }),
      });

      const json = await res.json();

      if (!res.ok || json.error) {
        stopLoader();
        outputBody.innerHTML = `<div style="color:var(--danger);padding:1rem;">
          ⚠️ Error: ${json.error || 'Unknown error. Please try again.'}
        </div>`;
        return;
      }

      stopLoader();
      renderArticle(json.article);

    } catch (err) {
      stopLoader();
      outputBody.innerHTML = `<div style="color:var(--danger);padding:1rem;">
        ⚠️ Network error: ${err.message}
      </div>`;
    } finally {
      generateBtn.disabled = false;
    }
  });

  // ── Render article output ──────────────────────────────────
  function renderArticle(art) {
    const seoHtml = `
      ${art.meta_description ? `
        <div class="seo-box">
          <div class="seo-label">Meta Description</div>
          <p>${escHtml(art.meta_description)}</p>
        </div>` : ''}
      ${art.seo_keywords ? `
        <div class="seo-box" style="margin-bottom:1.5rem;">
          <div class="seo-label">SEO Keywords</div>
          <p>${escHtml(art.seo_keywords)}</p>
        </div>` : ''}
    `;

    outputBody.innerHTML = `
      <div id="articleContent">
        <div class="article-body">
          ${seoHtml}
          ${art.content}
        </div>
      </div>
    `;

    outputToolbar.style.display = 'flex';

    // Show edit link if we got a saved ID
    if (art.id) {
      editBtn.href = `/article/${art.id}/edit`;
      editBtn.style.display = 'inline-flex';
    }
  }

  // ── Copy ───────────────────────────────────────────────────
  copyBtn.addEventListener('click', function () {
    const el = document.getElementById('articleContent');
    if (!el) return;
    navigator.clipboard.writeText(el.innerText).then(function () {
      copyBtn.textContent = '✅ Copied!';
      setTimeout(function () { copyBtn.textContent = '📋 Copy'; }, 2000);
    });
  });

  // ── PDF (print) ────────────────────────────────────────────
  pdfBtn.addEventListener('click', function () {
    window.print();
  });

  // ── Helper: escape HTML ────────────────────────────────────
  function escHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Hide sidebar and toolbar in print
  const printStyle = document.createElement('style');
  printStyle.textContent = `
    @media print {
      .sidebar, .topbar, .gen-panel, .output-toolbar { display: none !important; }
      .main-content { margin-left: 0 !important; }
      .generate-layout { display: block !important; }
      .page-content { padding: 0 !important; }
    }
  `;
  document.head.appendChild(printStyle);

})();
