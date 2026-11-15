#!/usr/bin/env python3
# smoke test : fait tourner chaque module avec des inputs fifos, capture les erreurs
import sys, io, builtins, traceback
sys.path.insert(0, "/Users/mleal/Desktop/FlashToolSuper/modules")
import osint, recon, phish, system

RESULTS = []
def t(name, fn, inputs):
    it = iter(inputs)
    builtins.input = lambda *a: next(it)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn()
        RESULTS.append((name, "OK", ""))
    except Exception as e:
        RESULTS.append((name, "FAIL", f"{type(e).__name__}: {e}"))
    finally:
        sys.stdout = old
        builtins.input = input

t("username_hunt", osint.username_hunt, ["rick"])
t("whois", osint.whois, ["example.com"])
t("dns_enum", osint.dns_enum, ["example.com"])
t("subdomains", osint.subdomains, ["github.com"])
t("geoloc", osint.geoloc, ["1.1.1.1"])
t("reverse_ip", osint.reverse_ip, ["1.1.1.1"])
t("wayback", osint.wayback, ["example.com"])
t("pastes", osint.pastes, ["test"])
t("permutator", osint.permutator, ["jean", "dupont", "exemple.com"])
t("tls_info", osint.tls_info, ["github.com"])
t("breach", osint.breach, ["test@example.com"])

t("pubip", recon.pubip, [])
t("arp", recon.arp, [])
t("routes", recon.routes, [])
t("wifi_mine", recon.wifi_mine, [])
t("wifi_scan", recon.wifi_scan, [])
t("dns_leak", recon.dns_leak, [])
t("port_scan", recon.port_scan, ["github.com", "443"])

t("pretext_email", phish.pretext_email, ["banque.com", "alerte@x.com"])
t("pretext_sms", phish.pretext_sms, [])
t("dork_gen", phish.dork_gen, ["exemple.com"])
t("login_page", phish.login_page, ["Webmail Test"])
t("link_tracker", phish.link_tracker, ["https://example.com"])

t("procs", system.procs, [])
t("agents", system.agents, [])
t("ports", system.ports, [])
t("disk", system.disk, [])
t("history", system.history, [])
t("hw", system.hw, [])

for name, st, err in RESULTS:
    print(f"{st:<5} {name:<16} {err}")
print(f"\n{sum(1 for _,s,_ in RESULTS if s=='OK')}/{len(RESULTS)} OK")
