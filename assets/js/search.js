(async function () {
  const params = new URLSearchParams(location.search);
  const selected = {
    categories: new Set(readParam('categories')),
    tags: new Set(readParam('tags')),
  };
  const input = document.querySelector('#search-input');
  input.value = params.get('q') || '';
  const articles = await fetch('/index.json').then((response) => response.json());

  function readParam(name) {
    return (params.get(name) || '').split(',').map((value) => value.trim()).filter(Boolean);
  }

  function updateUrl() {
    for (const name of ['categories', 'tags']) {
      const values = [...selected[name]];
      values.length ? params.set(name, values.join(',')) : params.delete(name);
    }
    input.value.trim() ? params.set('q', input.value.trim()) : params.delete('q');
    history.replaceState(null, '', `${location.pathname}${params.size ? `?${params}` : ''}`);
  }

  function toggle(name, value) {
    selected[name].has(value) ? selected[name].delete(value) : selected[name].add(value);
    updateUrl();
    render();
  }

  function renderFilters(name, values, label) {
    const container = document.querySelector(`#${name === 'categories' ? 'category' : 'tag'}-filters`);
    container.replaceChildren();
    const heading = document.createElement('span');
    heading.textContent = `${label}：`;
    container.append(heading);
    for (const value of values) {
      const button = document.createElement('button');
      button.textContent = value;
      button.classList.toggle('active', selected[name].has(value));
      button.addEventListener('click', () => toggle(name, value));
      container.append(button);
    }
  }

  function matches(article) {
    const categoryMatch = !selected.categories.size || article.categories.some((value) => selected.categories.has(value));
    const tagMatch = !selected.tags.size || article.tags.some((value) => selected.tags.has(value));
    const text = `${article.title} ${article.categories.join(' ')} ${article.tags.join(' ')}`.toLowerCase();
    return categoryMatch && tagMatch && text.includes(input.value.trim().toLowerCase());
  }

  function render() {
    renderFilters('categories', [...new Set(articles.flatMap((article) => article.categories))].sort(), '分类');
    renderFilters('tags', [...new Set(articles.flatMap((article) => article.tags))].sort(), '标签');
    const filtered = articles.filter(matches);
    document.querySelector('#search-summary').textContent = `找到 ${filtered.length} 篇文章`;
    const results = document.querySelector('#search-results');
    results.replaceChildren();
    for (const article of filtered) {
      const item = document.createElement('article');
      const date = document.createElement('time');
      date.textContent = article.created;
      const title = document.createElement('h2');
      const link = document.createElement('a');
      link.href = article.url;
      link.textContent = article.title;
      title.append(link);
      const meta = document.createElement('p');
      meta.textContent = [...article.categories, ...article.tags].join(' · ');
      item.append(date, title, meta);
      results.append(item);
    }
  }

  input.addEventListener('input', () => {
    updateUrl();
    render();
  });
  render();
})();
