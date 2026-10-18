(function () {
  const backToTop = document.querySelector('.back-to-top');
  let firstGAt = 0;

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function isEditing(target) {
    return target instanceof HTMLElement &&
      (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName));
  }

  backToTop.addEventListener('click', scrollToTop);
  window.addEventListener('scroll', () => {
    backToTop.classList.toggle('visible', window.scrollY > 320);
  }, { passive: true });

  document.addEventListener('keydown', (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey || isEditing(event.target)) return;

    if (event.key === 'j') {
      window.scrollBy({ top: 80, behavior: 'smooth' });
    } else if (event.key === 'k') {
      window.scrollBy({ top: -80, behavior: 'smooth' });
    } else if (event.key === 'G') {
      window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
    } else if (event.key === 'g') {
      const now = Date.now();
      if (now - firstGAt < 600) scrollToTop();
      firstGAt = now;
    } else {
      firstGAt = 0;
      return;
    }

    event.preventDefault();
  });
})();
