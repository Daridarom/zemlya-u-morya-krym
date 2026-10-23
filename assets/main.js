// Прототип: форма проверяет поля, но заявку никуда не отправляет.
// На рабочем домене сюда подключается обработчик на российском хостинге (152-ФЗ):
// задайте адрес в FORM_ENDPOINT, и форма начнёт отправлять заявки.
const FORM_ENDPOINT = '';

(function () {
  const form = document.getElementById('req-form');
  const msg = document.getElementById('form-msg');

  // Метки рекламы сохраняем, чтобы заявка знала, с какого объявления пришёл человек
  const params = new URLSearchParams(location.search);
  const utm = {};
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid'].forEach(function (k) {
    if (params.get(k)) utm[k] = params.get(k);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    msg.classList.remove('err');
    const phone = form.phone.value.replace(/\D/g, '');
    if (phone.length < 10) {
      msg.textContent = 'Проверьте номер: нужно 10–11 цифр.';
      msg.classList.add('err');
      form.phone.focus();
      return;
    }
    if (!form.consent.checked) {
      msg.textContent = 'Отметьте согласие на обработку данных, иначе я не смогу ответить.';
      msg.classList.add('err');
      return;
    }
    const data = {
      phone: form.phone.value,
      product: form.product.value,
      channel: form.channel.value,
      page: location.href,
      utm: utm
    };
    if (!FORM_ENDPOINT) {
      msg.textContent = 'Это прототип: заявка не отправлена. Позвоните +7 978 296-41-08 или напишите в MAX.';
      return;
    }
    fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) {
        if (!r.ok) throw new Error();
        msg.textContent = 'Заявка отправлена. Свяжусь с вами в ближайшее время.';
        form.reset();
      })
      .catch(function () {
        msg.textContent = 'Заявка не ушла. Позвоните +7 978 296-41-08 или напишите в MAX.';
        msg.classList.add('err');
      });
  });

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
