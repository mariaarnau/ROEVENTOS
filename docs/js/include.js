/* Carga header y footer compartidos (partials/) e inicializa el estado del nav.
   Requiere servir el sitio por HTTP (ver README/instrucciones de arranque). */
(function () {
  async function include(selector, url) {
    const host = document.querySelector(selector);
    if (!host) return;
    try {
      const res = await fetch(url);
      host.innerHTML = await res.text();
    } catch (e) {
      console.error('No se pudo cargar ' + url + '. Sirve el sitio con un servidor local (no abras el HTML con file://).', e);
    }
  }

  function markActiveNav() {
    const page = document.body.getAttribute('data-page');
    document.querySelectorAll('.main-nav a[data-page]').forEach(a => {
      if (a.getAttribute('data-page') === page) a.classList.add('is-active');
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([
      include('[data-include="header"]', 'partials/header.html'),
      include('[data-include="footer"]', 'partials/footer.html'),
    ]);
    markActiveNav();
    document.dispatchEvent(new CustomEvent('partials:ready'));
  });
})();
