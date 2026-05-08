/**
 * NeuraPulse — Privacy Policy Popup
 * ===================================
 * Intercepts ALL clicks on privacy policy links across the site
 * and shows the policy inside a beautiful popup — no page reload,
 * no navigation away, works on every page automatically.
 *
 * Include once before </body>:
 *   <script src="/privacy-popup.js"></script>
 */

(function () {
  'use strict';

  // ── Styles ──────────────────────────────────────────────────────────────
  var css = `
    #np-privacy-overlay {
      position: fixed; inset: 0; z-index: 99999;
      background: rgba(0,0,0,0.85);
      backdrop-filter: blur(8px);
      display: flex; align-items: center; justify-content: center;
      opacity: 0; visibility: hidden;
      transition: opacity 0.35s ease, visibility 0.35s ease;
    }
    #np-privacy-overlay.np-open {
      opacity: 1; visibility: visible;
    }
    #np-privacy-box {
      background: #0c1120;
      border: 1px solid #00e5ff;
      border-radius: 16px;
      width: 92%; max-width: 720px;
      max-height: 85vh;
      display: flex; flex-direction: column;
      box-shadow: 0 0 60px rgba(0,229,255,0.15);
      transform: translateY(28px);
      transition: transform 0.35s ease;
      overflow: hidden;
    }
    #np-privacy-overlay.np-open #np-privacy-box {
      transform: translateY(0);
    }
    #np-privacy-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1.1rem 1.5rem;
      background: linear-gradient(135deg, #111827, #1a0d3d);
      border-bottom: 1px solid #1e2d45;
      flex-shrink: 0;
    }
    #np-privacy-header span {
      font-family: 'Syne', sans-serif;
      font-size: 1.05rem; font-weight: 700;
      color: #e2e8f0;
    }
    #np-privacy-close {
      background: none; border: none; cursor: pointer;
      color: #64748b; font-size: 1.4rem; line-height: 1;
      transition: color 0.2s; padding: 0;
    }
    #np-privacy-close:hover { color: #00e5ff; }
    #np-privacy-body {
      overflow-y: auto; padding: 1.5rem 2rem;
      flex: 1;
      scrollbar-width: thin;
      scrollbar-color: #1e2d45 transparent;
    }
    #np-privacy-body::-webkit-scrollbar { width: 4px; }
    #np-privacy-body::-webkit-scrollbar-thumb { background: #1e2d45; border-radius: 2px; }
    #np-privacy-loading {
      text-align: center; padding: 3rem;
      font-family: 'Space Mono', monospace;
      font-size: 0.8rem; color: #64748b;
      letter-spacing: 0.1em;
    }
    #np-privacy-footer {
      padding: 1rem 1.5rem;
      border-top: 1px solid #1e2d45;
      display: flex; justify-content: flex-end; gap: 0.75rem;
      flex-shrink: 0;
    }
    .np-pp-btn {
      font-family: 'Space Mono', monospace;
      font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
      padding: 0.6rem 1.4rem; border-radius: 4px;
      cursor: pointer; border: none; transition: all 0.2s;
      text-decoration: none; display: inline-block;
    }
    .np-pp-btn-primary { background: #00e5ff; color: #050810; }
    .np-pp-btn-primary:hover { box-shadow: 0 0 20px rgba(0,229,255,0.4); }
    .np-pp-btn-secondary { background: transparent; color: #64748b; border: 1px solid #1e2d45; }
    .np-pp-btn-secondary:hover { border-color: #00e5ff; color: #00e5ff; }
    /* Mobile */
    @media (max-width: 600px) {
      #np-privacy-box { width: 100%; max-width: 100%; border-radius: 16px 16px 0 0; max-height: 90vh; position: fixed; bottom: 0; }
      #np-privacy-overlay { align-items: flex-end; }
      #np-privacy-body { padding: 1rem 1.2rem; }
    }
  `;

  // ── Inject styles ────────────────────────────────────────────────────────
  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Build popup HTML ─────────────────────────────────────────────────────
  var overlay = document.createElement('div');
  overlay.id = 'np-privacy-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Privacy Policy');
  overlay.innerHTML = `
    <div id="np-privacy-box">
      <div id="np-privacy-header">
        <span>🔒 Privacy Policy</span>
        <button id="np-privacy-close" aria-label="Close">✕</button>
      </div>
      <div id="np-privacy-body">
        <div id="np-privacy-loading">Loading privacy policy…</div>
      </div>
      <div id="np-privacy-footer">
        <button class="np-pp-btn np-pp-btn-secondary" id="np-pp-close-btn">Close</button>
        <a class="np-pp-btn np-pp-btn-primary" href="/privacy-policy.html" target="_blank" rel="noopener">
          Open Full Page ↗
        </a>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  // ── State ────────────────────────────────────────────────────────────────
  var contentLoaded = false;

  function openPopup() {
    overlay.classList.add('np-open');
    document.body.style.overflow = 'hidden';
    document.getElementById('np-privacy-close').focus();

    if (!contentLoaded) {
      loadContent();
    }
  }

  function closePopup() {
    overlay.classList.remove('np-open');
    document.body.style.overflow = '';
  }

  function loadContent() {
    fetch('/privacy-policy.html')
      .then(function (r) { return r.text(); })
      .then(function (html) {
        // Extract just the <main> or <body> content
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        var main = doc.querySelector('main') || doc.querySelector('.wrap') || doc.body;

        // Remove nav/footer/scripts from extracted content
        ['nav', 'footer', 'script', 'style', '.popup-overlay', '#np-btn', '#np-win'].forEach(function (sel) {
          main.querySelectorAll(sel).forEach(function (el) { el.remove(); });
        });

        var body = document.getElementById('np-privacy-body');
        body.innerHTML = main.innerHTML;

        // Override inline styles for dark theme readability
        body.style.cssText = 'color:#e2e8f0; font-family:"DM Sans",sans-serif; font-size:0.95rem; line-height:1.8;';
        body.querySelectorAll('h1,h2,h3,h4').forEach(function (h) {
          h.style.color = '#00e5ff';
          h.style.fontFamily = "'Syne', sans-serif";
        });
        body.querySelectorAll('a').forEach(function (a) {
          a.style.color = '#00e5ff';
        });

        contentLoaded = true;
      })
      .catch(function () {
        document.getElementById('np-privacy-body').innerHTML =
          '<p style="color:#94a3b8;font-family:\'DM Sans\',sans-serif;padding:1rem 0;">Unable to load privacy policy inline. ' +
          '<a href="/privacy-policy.html" target="_blank" style="color:#00e5ff;">Click here to open it</a>.</p>';
      });
  }

  // ── Event listeners ──────────────────────────────────────────────────────
  document.getElementById('np-privacy-close').addEventListener('click', closePopup);
  document.getElementById('np-pp-close-btn').addEventListener('click', closePopup);

  // Close on overlay background click
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePopup();
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePopup();
  });

  // ── Intercept ALL privacy policy link clicks ─────────────────────────────
  document.addEventListener('click', function (e) {
    var el = e.target;
    // Walk up to find anchor tag
    while (el && el.tagName !== 'A') { el = el.parentElement; }
    if (!el) return;

    var href = el.getAttribute('href') || '';
    var text = el.textContent || '';

    var isPrivacyLink = (
      /privacy/i.test(href) ||
      /privacy/i.test(text)
    );

    if (isPrivacyLink) {
      e.preventDefault();
      e.stopPropagation();
      openPopup();
    }
  }, true); // capture phase so form doesn't submit first

})();
