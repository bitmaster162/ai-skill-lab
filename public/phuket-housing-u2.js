/* U2 progressive enhancement: local DOM only. No network, storage or URL writes. */
(() => {
  function initializeHousingFilters() {
  'use strict';
  const root = document.querySelector('[data-u2-catalog]');
  if (!root || root.dataset.u2Ready === 'true') return;
  const status = root.querySelector('[data-u2-status]');
  const type = root.querySelector('#pu-type');
  const beds = root.querySelector('#pu-beds');
  const price = root.querySelector('#pu-price');
  const applyButton = root.querySelector('[data-u2-apply]');
  const deals = [...root.querySelectorAll('[data-u2-deal]')];
  const areas = [...root.querySelectorAll('[data-u2-area]')];
  const cards = [...root.querySelectorAll('[data-u2-card]')];
  if (!status || !type || !beds || !price || !applyButton || deals.length !== 2 || areas.length !== 8) return;
  const english = document.documentElement.lang === 'en';
  let deal = 'rent';
  let area = '';
  const amount = (value) => {
    if (value === '') return Infinity;
    if (!/^\d{1,12}(?:\.\d{1,2})?$/.test(value)) return NaN;
    const [whole, fraction = ''] = value.split('.');
    return Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  };
  const render = () => {
    const cap = amount(price.value);
    const invalid = Number.isNaN(cap) || price.validity.badInput;
    price.setAttribute('aria-invalid', String(invalid));
    let count = 0;
    for (const card of cards) {
      const d = card.dataset;
      const wantedBeds = beds.value;
      const bedroomMatch = wantedBeds === '' || (wantedBeds === '4+' ? Number(d.beds) >= 4 : Number(d.beds) === Number(wantedBeds));
      const visible = !invalid && d.deal === deal && (!area || d.area === area)
        && (!type.value || d.type === type.value) && bedroomMatch && Number(d.price) <= cap;
      card.hidden = !visible;
      if (visible) count += 1;
    }
    for (const button of deals) button.setAttribute('aria-pressed', String(button.dataset.u2Deal === deal));
    for (const button of areas) button.setAttribute('aria-pressed', String(button.dataset.u2Area === area));
    status.textContent = invalid
      ? (english ? 'Enter a non-negative price with up to two decimals.' : 'Введите неотрицательную цену, не более двух знаков после запятой.')
      : count ? (english ? `Listings: ${count}` : `Объектов: ${count}`)
        : cards.length ? (english ? 'No listings match these filters.' : 'По этим фильтрам объектов нет.')
          : (english ? 'Coming soon: agencies are adding homes.' : 'Скоро: агентства добавляют объекты.');
  };
  for (const button of deals) button.addEventListener('click', () => { deal = button.dataset.u2Deal; render(); });
  for (const button of areas) button.addEventListener('click', () => { area = button.dataset.u2Area; render(); });
  for (const field of [type, beds, price]) field.addEventListener('change', render);
  applyButton.addEventListener('click', render);
  render();
  for (const control of [...deals, ...areas, type, beds, price, applyButton]) {
    control.disabled = false;
    control.removeAttribute('aria-disabled');
  }
  root.dataset.u2Ready = 'true';
  }
  document.addEventListener('phuket-housing:ready', initializeHousingFilters);
  initializeHousingFilters();
})();
