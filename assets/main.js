(function () {
  // Метки рекламы передаём в скрытые поля Яндекс Формы, чтобы в заявке было видно, с какого объявления пришёл человек
  const params = new URLSearchParams(location.search);
  const frame = document.getElementById('ya-form');
  if (frame) {
    const src = new URL(frame.getAttribute('src'));
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid'].forEach(function (k) {
      if (params.get(k)) src.searchParams.set(k, params.get(k));
    });
    if (src.toString() !== frame.getAttribute('src')) frame.setAttribute('src', src.toString());
  }

  // Галерея и кадастровые схемы: полный кадр без обрезки.
  // Никакие данные пользователя здесь не сохраняются и не отправляются.
  const viewer = document.getElementById('image-viewer');
  const viewerImg = document.getElementById('viewer-img');
  const viewerCaption = document.getElementById('viewer-caption');
  const viewerClose = viewer && viewer.querySelector('.viewer-close');
  if (viewer && viewerImg && viewerClose && typeof viewer.showModal === 'function') {
    document.querySelectorAll('.photo-open').forEach(function (button) {
      button.addEventListener('click', function () {
        const img = button.querySelector('img');
        if (!img) return;
        viewerImg.src = img.currentSrc || img.src;
        viewerImg.alt = img.alt;
        viewerCaption.textContent = img.alt;
        viewer.showModal();
      });
    });
    viewerClose.addEventListener('click', function () { viewer.close(); });
    viewer.addEventListener('click', function (event) {
      if (event.target === viewer) viewer.close();
    });
    viewer.addEventListener('close', function () {
      viewerImg.removeAttribute('src');
      viewerImg.alt = '';
    });
  }

  // Нижняя кнопка на телефоне прячется на первом экране и когда форма уже видна
  const sticky = document.querySelector('.sticky-cta');
  const watched = [document.querySelector('.hero'), document.getElementById('zayavka')];
  if ('IntersectionObserver' in window && sticky) {
    const visible = new Set();
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.isIntersecting ? visible.add(en.target) : visible.delete(en.target); });
      sticky.classList.toggle('hide', visible.size > 0);
    });
    watched.forEach(function (el) { if (el) io.observe(el); });
  }
})();
