/* Interacciones de la maqueta: menú móvil, header al hacer scroll,
   animaciones reveal, contadores, barras de progreso, slider de
   testimonios y acordeón de tarjetas de eventos. */
(function () {

  function initHeader() {
    const header = document.getElementById('siteHeader');
    const toggle = document.getElementById('navToggle');
    const nav = document.getElementById('mainNav');
    if (!header) return;

    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    if (toggle && nav) {
      toggle.addEventListener('click', () => {
        const open = nav.classList.toggle('is-open');
        toggle.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', String(open));
      });
      nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
        nav.classList.remove('is-open');
        toggle.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }));
    }
  }

  function initReveal() {
    const items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(el => el.classList.add('is-visible'));
      return;
    }

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
    items.forEach(el => obs.observe(el));

    /* Red de seguridad: si por lo que sea el observer no llega a disparar
       (scroll muy rápido, viewport atípico, captura automática de
       pantalla...) el contenido nunca debe quedarse invisible. */
    window.setTimeout(() => {
      items.forEach(el => el.classList.add('is-visible'));
    }, 2000);
  }

  function initCounters() {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;
    const animate = (el) => {
      const target = parseInt(el.getAttribute('data-count'), 10);
      const suffix = el.getAttribute('data-suffix') || '';
      const duration = 1600;
      const start = performance.now();
      const step = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased).toLocaleString('es-ES') + suffix;
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    const done = new Set();
    const runOnce = (el) => {
      if (done.has(el)) return;
      done.add(el);
      animate(el);
    };
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          runOnce(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach(el => obs.observe(el));

    /* Red de seguridad, igual que en initReveal(). */
    window.setTimeout(() => counters.forEach(runOnce), 2200);
  }

  function initProgressBars() {
    const bars = document.querySelectorAll('.progress-fill');
    if (!bars.length) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = entry.target.getAttribute('data-value') || '0';
          entry.target.style.width = target + '%';
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    bars.forEach(el => obs.observe(el));

    /* Red de seguridad, igual que en initReveal(). */
    window.setTimeout(() => {
      bars.forEach(el => {
        if (!el.style.width) el.style.width = (el.getAttribute('data-value') || '0') + '%';
      });
    }, 2200);
  }

  function initTestimonials() {
    const slider = document.querySelector('.testimonial-slider');
    if (!slider) return;
    const slides = slider.querySelectorAll('.testimonial-slide');
    const dotsWrap = slider.querySelector('.testimonial-dots');
    const prevBtn = slider.querySelector('.tn-prev');
    const nextBtn = slider.querySelector('.tn-next');
    let index = 0;
    let timer;

    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      if (i === 0) dot.classList.add('is-active');
      dot.addEventListener('click', () => go(i));
      dotsWrap.appendChild(dot);
    });
    const dots = dotsWrap.querySelectorAll('button');

    function go(i) {
      slides[index].classList.remove('is-active');
      dots[index].classList.remove('is-active');
      index = (i + slides.length) % slides.length;
      slides[index].classList.add('is-active');
      dots[index].classList.add('is-active');
      resetTimer();
    }
    function resetTimer() {
      clearInterval(timer);
      timer = setInterval(() => go(index + 1), 6500);
    }
    prevBtn.addEventListener('click', () => go(index - 1));
    nextBtn.addEventListener('click', () => go(index + 1));
    resetTimer();
  }

  function initEventAccordion() {
    document.querySelectorAll('.event-detail-toggle').forEach(btn => {
      const panel = btn.closest('.event-body').querySelector('.event-detail-panel');
      if (!panel) return;
      btn.addEventListener('click', () => {
        const isOpen = btn.classList.toggle('is-open');
        panel.style.maxHeight = isOpen ? panel.scrollHeight + 'px' : '0px';
      });
    });
  }

  function initContactForms() {
    document.querySelectorAll('form[data-preview-form]').forEach(form => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const success = form.parentElement.querySelector('.form-success');
        if (success) success.classList.add('is-visible');
        form.reset();
      });
    });
  }

  document.addEventListener('partials:ready', initHeader);
  document.addEventListener('DOMContentLoaded', () => {
    initReveal();
    initCounters();
    initProgressBars();
    initTestimonials();
    initEventAccordion();
    initContactForms();
  });
})();
