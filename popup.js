// ===== NEURAPLUS POPUP SCRIPT =====
// Inject popup HTML into every page automatically
(function () {
  const html = `
  <div class="np-popup-overlay" id="npPopupOverlay">
    <div class="np-popup-box">
      <button class="np-popup-close" id="npPopupClose">✕</button>
      <div id="npPopupContent">
        <div class="np-popup-tag">🔔 Stay Connected</div>
        <h2 class="np-popup-title">Get Free AI Insights Every Week</h2>
        <p class="np-popup-sub">Join thousands of AI enthusiasts. Get the latest AI news, tools, and insights delivered to your inbox — free forever.</p>
        <form class="np-popup-form" id="npPopupForm">
          <div class="np-form-group">
            <label>Your Name *</label>
            <input type="text" name="name" placeholder="Your name" required>
          </div>
          <div class="np-form-group">
            <label>Email Address *</label>
            <input type="email" name="email" placeholder="you@email.com" required>
          </div>
          <div class="np-form-group">
            <label>Phone Number</label>
            <input type="tel" name="phone" placeholder="+91 90000 00000">
          </div>
          <input type="hidden" name="_subject" value="New Popup Subscriber — NeuraPulse">
          <div class="np-popup-checkbox">
            <input type="checkbox" id="npPopupPrivacy" required>
            <label for="npPopupPrivacy">I agree to the <a href="#" target="_blank">Privacy Policy</a> and consent to receive emails from NeuraPulse. I can unsubscribe anytime.</label>
          </div>
          <button type="submit" class="np-popup-btn" id="npPopupSubmitBtn">Subscribe Free →</button>
        </form>
      </div>
      <div class="np-popup-success" id="npPopupSuccess">
        <h3>🎉 Thank You!</h3>
        <p>You're now subscribed to NeuraPulse. Check your inbox for a confirmation email!</p>
      </div>
    </div>
  </div>`;

  // Insert popup into page
  document.body.insertAdjacentHTML('afterbegin', html);

  const overlay   = document.getElementById('npPopupOverlay');
  const closeBtn  = document.getElementById('npPopupClose');
  const form      = document.getElementById('npPopupForm');
  const submitBtn = document.getElementById('npPopupSubmitBtn');
  const content   = document.getElementById('npPopupContent');
  const success   = document.getElementById('npPopupSuccess');

  let popupShown = false;

  function showPopup() {
    if (!popupShown) {
      overlay.classList.add('active');
      popupShown = true;
    }
  }

  function closePopup() {
    overlay.classList.remove('active');
    popupShown = false;
    // Re-show after 5 minutes
    setTimeout(showPopup, 300000);
  }

  // Close on X button
  closeBtn.addEventListener('click', closePopup);

  // Close on overlay background click
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePopup();
  });

  // Close on ESC key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePopup();
  });

  // Show popup after 5 minutes (300000ms)
  // Change to 10000 for 10 seconds to test
  setTimeout(showPopup, 300000);

  // Form submit
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    submitBtn.textContent = 'Sending...';
    submitBtn.style.opacity = '0.7';
    submitBtn.style.pointerEvents = 'none';

    fetch('https://formspree.io/f/xzdogyvo', {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    })
    .then(function (r) {
      if (r.ok) {
        content.style.display = 'none';
        success.style.display = 'block';
        setTimeout(function () {
          closePopup();
          setTimeout(function () {
            content.style.display = 'block';
            success.style.display = 'none';
            form.reset();
            submitBtn.textContent = 'Subscribe Free →';
            submitBtn.style.opacity = '1';
            submitBtn.style.pointerEvents = 'auto';
          }, 500);
        }, 3000);
      } else {
        submitBtn.textContent = 'Try Again';
        submitBtn.style.opacity = '1';
        submitBtn.style.pointerEvents = 'auto';
      }
    })
    .catch(function () {
      submitBtn.textContent = 'Try Again';
      submitBtn.style.opacity = '1';
      submitBtn.style.pointerEvents = 'auto';
    });
  });

})();
