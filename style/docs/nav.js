/**
 * Page Navigation for Decktape
 * Generic navigation script for PDF rendering
 *
 * Usage:
 *   <script src="nav.js"></script>
 *   <script src="nav.js" data-selector=".page"></script>
 *   <script src="nav.js" data-selector=".slide"></script>
 */

(function () {
  const script = document.currentScript;
  const selector = script?.dataset?.selector || '.page, .slide';
  const pages = document.querySelectorAll(selector);

  if (pages.length === 0) return;

  let current = 0;

  // Initialize: hide all but first
  pages.forEach((p, i) => {
    if (i === 0) {
      p.classList.add('active');
    } else {
      p.style.display = 'none';
    }
  });

  // Arrow key navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' && current < pages.length - 1) {
      pages[current].style.display = 'none';
      pages[current].classList.remove('active');
      current++;
      pages[current].style.display = '';
      pages[current].classList.add('active');
    }
    if (e.key === 'ArrowLeft' && current > 0) {
      pages[current].style.display = 'none';
      pages[current].classList.remove('active');
      current--;
      pages[current].style.display = '';
      pages[current].classList.add('active');
    }
  });
})();
