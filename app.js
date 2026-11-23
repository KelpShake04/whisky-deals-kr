(() => {
  const tabs = document.querySelectorAll('.tab-btn');
  const cards = document.querySelectorAll('.deal-card');
  const searchInput = document.getElementById('search-input');
  const emptyState = document.getElementById('empty-state');

  let activeCategory = 'all';

  function applyFilter() {
    const q = (searchInput?.value || '').trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const cat = card.dataset.category || '';
      const text = (card.textContent || '').toLowerCase();
      const catMatch = activeCategory === 'all' || cat === activeCategory;
      const queryMatch = !q || text.includes(q);
      const show = catMatch && queryMatch;
      card.style.display = show ? 'flex' : 'none';
      if (show) visible += 1;
    });

    if (emptyState) {
      emptyState.style.display = visible === 0 ? 'block' : 'none';
    }
  }

  tabs.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabs.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.dataset.category || 'all';
      applyFilter();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', applyFilter);
  }
})();
