# dc_fullscreen.py — LA BIBLIOTHÈQUE FULLSCREEN · powered by Maxime Leal

Les animations qui **remplissent TOUTE la fenêtre du terminal** — 80x24 ou 300x80, elles
s'adaptent automatiquement via `os.get_terminal_size()`. Plus jamais de petites animations
coinçées dans un coin : chaque animation couvre tout l'écran.

## LES 20 ANIMATIONS FULLSCREEN
| Nom | Personnage | Animation |
|---|---|---|
| `batman_intro` | Batman | bat-signal qui balaie TOUT le ciel + chauve-souris géante centrée |
| `flash_intro` | Flash | lignes de vitesse FULLSCREEN + éclair qui descend + titre centré |
| `joker_intro` | Joker | HAHA envahit TOUT l'écran + carte Joker centrée |
| `matrix_rain_fullscreen` | Matrice | LA pluie de code remplit TOUTES les colonnes du terminal |
| `star_scanlines` | S.T.A.R. Labs | scanlines bleu holographique + particules full-screen |
| `lex_boot_fullscreen` | Lex Luthor | ondes vertes corporate qui pulsent |
| `lasso_fullscreen` | Wonder Woman | lasso doré + cercles concentriques qui tournent |
| `waves_fullscreen` | Aquaman | vagues turquoise + bulles qui montent |
| `candle_fullscreen` | Constantine | bougie + fumée qui remplit tout |
| `raven_fullscreen` | Raven | fumée violette + ombres |
| `war_gears_fullscreen` | WarWorld | rouages de guerre qui envahissent tout |
| `superman_fullscreen` | Superman | le S traverse + étoiles |
| `globe_fullscreen` | Daily Planet | globe qui tourne + étoiles |
| `scarecrow_fullscreen` | Scarecrow | fumée orange épouvantail |
| `catwoman_fullscreen` | Catwoman | bijoux scintillants |
| `hive_fullscreen` | H.I.V.E. | abeilles qui convergent vers la ruche |
| `cyborg_fullscreen` | Cyborg | scanlines + circuits |
| `alert_fullscreen` | — | alerte rouge plein écran |
| `target_lock` | — | réticule qui converge (importable depuis WarWorld) |
| `fill_bg` | — | remplissage couleur plein écran |

## COMMENT UTILISER
```python
import dc_fullscreen as fs
fs.hid()
fs.batman_intro(4.0)          # remplit tout l'écran
fs.flash_intro(3.5)           # le flash
fs.matrix_rain_fullscreen(4.0)# la pluie de code fullscreen
fs.show()                     # affiche le curseur
```

## CHAQUE KIT PEUT UTILISER
```python
import dc_fullscreen as fs
# au lancement :
fs.batman_intro(3.0)     # ou fs.flash_intro / fs.joker_intro / etc.
# entre les écrans :
fs.batman_transition()   # chauve-souris rapide
# pour un tool spécifique :
fs.matrix_rain_fullscreen(3.0)
```

## LA DIFFÉRENCE AVEC L'ANCIENNE VERSION
L'ancienne librairie dessinait dans un cadre 80x24 fixe — même en fullscreen, les
animations restaient dans leur coin. La v2 **lit la taille réelle du terminal** à chaque
animation (`os.get_terminal_size()`) et adapte toutes les coordonnées : les colonnes,
les rangées, le centre, les particules, tout s'étend sur toute la fenêtre. En fullscreen
(⌘+Ctrl+F), les animations remplissent littéralement tout l'écran.
