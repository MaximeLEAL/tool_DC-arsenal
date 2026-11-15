#!/usr/bin/env python3
# language: Python 3, file: dc_master.py, target: macOS
# LE BATCOMPUTER DE BUREAU - tous les kits DC depuis une seule console
import os, subprocess, sys

DESK = os.path.expanduser("~/Desktop/tool_DC")
KITS = [
    ("RickPortal (portail vert - kit malware complet)", "RickPortal",       "RickPortal.command"),
    ("FLASH TOOL_SUPER (eclair - 55 tools)",            "FlashToolSuper",   "python3 flash_tool.py"),
    ("BATCAVE (chauve-souris - investigation)",         "BatCave",          "python3 bat_tool.py"),
    ("JOKER (chaos - pranks)",                          "JokerChaos",       "python3 joker_tool.py"),
    ("AQUAMAN (trident - reseau)",                      "TridentAquaman",   "python3 aquaman_tool.py"),
    ("SUPERMAN (vision - systeme)",                     "SupermanVision",   "python3 superman_tool.py"),
    ("CONSTANTINE (ombre - dark web)",                  "ConstantineDark",  "python3 constantine_tool.py"),
    ("LASSO VERITE (verification)",                     "LassoVerite",      "python3 lasso_tool.py"),
    ("CYBORG (technet - integration)",                  "CyborgTech",       "python3 cyborg_tool.py"),
    ("LEXCORP (arsenal Windows)",                       "LexCorpIndustries","zsh verify_lex.zsh"),
    ("S.T.A.R. LABS (C2 DNS + framework + stealer)",    "STARLabs",         "python3 star_c2_server.py"),
    ("TASK FORCE X (deploiement SSH + APK)",            "TaskForceX",       "python3 taskforce_ssh_worm.py"),
    ("NEO - LA MATRICE (pluie de code)",                "NeoMatrix",        "python3 neo_tool.py"),
    ("LA FORCE (hyper-espace + defile)",                "ForceGalaxy",      "python3 force_tool.py"),
    ("CATWOMAN (voleuse de secrets)",                   "CatwomanVoleuse",  "python3 catwoman_tool.py"),
    ("ARKHAM - LE LEURRE (jeu + RAT Windows)",          "ArkhamGame",       "python3 lex_forge.py"),
    ("SCARECROW - L'EPOUVANTEUR (phishing 12 sites)",   "ScarecrowPhish",   "zsh trick_public.sh gmail"),
    ("DAILY PLANET (veille tech & cyber)",              "DailyPlanet",      "python3 veille.py serve"),
    ("WARWORLD - L'ARSENAL CYBER (registre 67 armes)",   "WarWorld",         "python3 warworld_cmd.py"),
    ("LIGNE ROUGE (orchestrateur de campagnes)",        "LeagueOfShadows",  "python3 league.py"),
    ("KRYPTONITE SUITE (scan IOCs -> Sigma/YARA)",      "KryptoniteSuite",  "python3 kryptonite.py scan"),
    ("W.O.P.R. (auto-lab CTF WarGames)",                "WOPR",             "python3 wopr.py play"),
    ("THE CALCULATOR (breach analytics)",               "TheCalculator",    "python3 calculator.py serve"),
    ("JOKER CARD - SGP (BadUSB + payloads de la carte)", "JokerCard",       "python3 joker_forge.py"),
    ("THE THINKER (reverse engineering lab)",           "TheThinker",       "python3 thinker.py arsenal"),
    ("RAVEN - EVASION EDR (syscalls/unhook/ETW/AMSI/sleep/stack)", "RavenEvasion", "zsh verify_raven.zsh"),
    ("LE BATCOMPUTER SUPRÊME (cockpit unique)",          "batcomputer_supreme", "python3 batcomputer_supreme.py"),
    ("H.I.V.E. (minage crypto)",                        "HiveMining",       "python3 ruche_tool.py"),
]

def draw():
    print("\033[2J\033[H")
    print("\033[1;97m" + "=" * 62)
    print("        LE BATCOMPUTER - 16 KITS DC - powered by Maxime Leal")
    print("=" * 62 + "\033[0m")
    for i, (name, folder, cmd) in enumerate(KITS):
        print(f"  \033[38;2;255;215;0m[{i+1:>2}]\033[0m {name}")
    print(f"\n  \033[38;2;255;215;0m[ catalogue ]\033[0m ouvre liste_tool.md   [q] quitter")

def main():
    while True:
        draw()
        c = input("\n  batcomputer> ").strip()
        if c.lower() == "q": return
        if c.lower() == "catalogue":
            subprocess.run(["open", os.path.join(DESK, "liste_tool.md")])
            continue
        if c.isdigit() and 1 <= int(c) <= len(KITS):
            name, folder, cmd = KITS[int(c) - 1]
            folder = os.path.join(DESK, folder)
            os.system("clear")
            if cmd.endswith(".command"):
                subprocess.run(["zsh", os.path.join(folder, cmd)])
            else:
                subprocess.run(["zsh", "-c", f"cd '{folder}' && {cmd}"])
            print("\n\033[2m[entree] retour au batcomputer\033[0m")
            input()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print()
