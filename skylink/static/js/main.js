// Skylink Corporate JavaScript
document.addEventListener('DOMContentLoaded', function () {
  // Mobile Navigation Menu Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileMenuClose = document.getElementById('mobile-menu-close');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', function () {
      mobileMenu.classList.toggle('hidden');
      document.body.classList.toggle('overflow-hidden');
    });
  }

  if (mobileMenuClose && mobileMenu) {
    mobileMenuClose.addEventListener('click', function () {
      mobileMenu.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    });
  }

  // Prevent double form submissions and display loading indicator
  const forms = document.querySelectorAll('form[data-prevent-double-submit]');
  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        if (submitBtn.dataset.submitting === 'true') {
          e.preventDefault();
          return false;
        }
        submitBtn.dataset.submitting = 'true';
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Processing & Saving...
        `;
        // Allow fallback timeout if server hangs
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.dataset.submitting = 'false';
          submitBtn.innerHTML = originalText;
        }, 15000);
      }
    });
  });

  // Auto-dismiss alert notifications after 6 seconds
  const alerts = document.querySelectorAll('.auto-dismiss-alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });
});
