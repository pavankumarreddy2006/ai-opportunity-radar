const text = (selector, value) => {
  document.querySelectorAll(selector).forEach((node) => {
    node.textContent = value;
  });
};

const showEmpty = (selector, message, detail) => {
  const node = document.querySelector(selector);
  if (!node) return;
  node.innerHTML = `<strong>${message}</strong><p>${detail}</p>`;
};

const formatDate = (value) => {
  if (!value) return "Waiting for updates";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Waiting for updates";
  return `${date.toISOString().slice(0, 16).replace("T", " ")} UTC`;
};

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const safeUrl = (value) => {
  try {
    const url = new URL(value, window.location.origin);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
  } catch {
    return "#";
  }
};

const fetchJson = async (path) => {
  const response = await fetch(path, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
};

const renderTopNews = (items) => {
  const list = document.querySelector("[data-top-news-list]");
  const empty = document.querySelector("[data-top-news-empty]");
  if (!list || !empty) return;

  if (!items.length) {
    empty.hidden = false;
    list.innerHTML = "";
    return;
  }

  empty.hidden = true;
  list.innerHTML = items
    .slice(0, 5)
    .map(
      (item, index) => `
        <a class="news-item" href="${safeUrl(item.link)}" target="_blank" rel="noopener noreferrer">
          <span class="rank">${index + 1}</span>
          <span class="news-body">
            <strong>${escapeHtml(item.raw_title)}</strong>
            <small>${escapeHtml(item.source)} / ${escapeHtml(item.category)}</small>
          </span>
          <span class="score">I ${escapeHtml(item.importance_score)} / O ${escapeHtml(item.opportunity_score)}</span>
        </a>
      `,
    )
    .join("");
};

const renderTopics = (groups) => {
  const list = document.querySelector("[data-topic-list]");
  const empty = document.querySelector("[data-topic-empty]");
  if (!list || !empty) return;

  if (!groups.length) {
    empty.hidden = false;
    list.innerHTML = "";
    return;
  }

  empty.hidden = true;
  list.innerHTML = groups
    .map(
      (group) => `
        <div class="topic-row">
          <span>${escapeHtml(group.section)}</span>
          <strong>${escapeHtml(group.signals?.length ?? 0)}</strong>
        </div>
      `,
    )
    .join("");
};

const hydrateDashboard = async () => {
  try {
    const health = await fetchJson("/health");
    text("[data-api-health]", "Healthy");
    text("[data-service-status]", health.status === "ok" ? "ONLINE" : "DEGRADED");
    text("[data-api-summary]", `AI News Collector API is healthy in ${health.environment} mode.`);
  } catch {
    text("[data-api-health]", "Degraded");
    text("[data-service-status]", "DEGRADED");
    text("[data-api-summary]", "The dashboard shell is online, but the health API did not respond.");
  }

  try {
    const topNews = await fetchJson("/top5");
    renderTopNews(topNews);
    text("[data-total-news]", String(topNews.length));
    text("[data-last-update]", formatDate(topNews[0]?.created_at));
  } catch {
    text("[data-total-news]", "Unavailable");
    showEmpty("[data-top-news-empty]", "Top news unavailable", "The /top5 endpoint did not return data.");
  }

  try {
    const trending = await fetchJson("/trending");
    renderTopics(trending);
    text("[data-trending-count]", String(trending.length));
  } catch {
    text("[data-trending-count]", "Unavailable");
    showEmpty("[data-topic-empty]", "Trends unavailable", "The /trending endpoint did not return data.");
  }
};

hydrateDashboard();
