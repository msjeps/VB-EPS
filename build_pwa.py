#!/usr/bin/env python3
"""
build_pwa.py — Génère pwa-build/index.html depuis VB_EPS.html
Modifications :
  1. Ajoute le lien vers manifest.json
  2. Ajoute les liens apple-touch-icon
  3. Remplace l'enregistrement SW blob par un SW externe (sw.js)
"""

import re, shutil, os

SRC  = os.path.join(os.path.dirname(__file__), "VB_EPS.html")
DEST = os.path.join(os.path.dirname(__file__), "pwa-build", "index.html")

# ── 1. Lecture du fichier source ──────────────────────────────────────────────
with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

# ── 2. Ajout manifest + apple-touch-icon après <meta name="theme-color"> ─────
MANIFEST_TAGS = (
    '\n<link rel="manifest" href="manifest.json">'
    '\n<link rel="apple-touch-icon" sizes="192x192" href="icon_192.png">'
    '\n<link rel="apple-touch-icon" sizes="512x512" href="icon_512.png">'
    '\n<link rel="shortcut icon" href="icon_192.png" type="image/png">'
)

# Cherche la balise theme-color et insère après
theme_pattern = r'(<meta name="theme-color"[^>]+>)'
if re.search(theme_pattern, html):
    html = re.sub(theme_pattern, r'\1' + MANIFEST_TAGS, html, count=1)
    print("✅ Balises manifest + apple-touch-icon ajoutées")
else:
    # Fallback : insérer avant </head>
    html = html.replace("</head>", MANIFEST_TAGS + "\n</head>", 1)
    print("⚠️  Insertion fallback avant </head>")

# ── 3. Remplacement du Service Worker blob par sw.js externe ─────────────────
SW_BLOB_PATTERN = r"if\s*\(\s*'serviceWorker'\s*in\s*navigator.*?navigator\.serviceWorker\.register\s*\(\s*swUrl\s*\)\s*;?\s*\}\s*catch.*?\}\s*\}"
SW_NEW_CODE = """if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => {
        // Vérifier les mises à jour
        reg.addEventListener('updatefound', () => {
          const newWorker = reg.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Nouvelle version disponible — on l'active immédiatement
              newWorker.postMessage({ type: 'SKIP_WAITING' });
            }
          });
        });
      })
      .catch(err => console.warn('SW registration failed:', err));
  });
}"""

# Tentative avec regex
match = re.search(SW_BLOB_PATTERN, html, re.DOTALL)
if match:
    html = html[:match.start()] + SW_NEW_CODE + html[match.end():]
    print("✅ Service Worker blob remplacé par sw.js")
else:
    # Fallback : chercher le bloc simple sur une zone connue
    OLD_SW = (
        "if('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {\n"
        "  try {\n"
        "    const swCode = "
    )
    idx = html.find("if('serviceWorker' in navigator")
    if idx != -1:
        # Trouver la fin du bloc (accolade fermante après le try/catch)
        end_idx = html.find("} catch(e) {}", idx)
        if end_idx != -1:
            end_idx += len("} catch(e) {}") + 1
            # Chercher la } finale du if
            next_brace = html.find("}", end_idx)
            if next_brace != -1:
                html = html[:idx] + SW_NEW_CODE + html[next_brace+1:]
                print("✅ Service Worker remplacé (fallback)")
            else:
                print("⚠️  Impossible de trouver la fin du bloc SW — remplacement non effectué")
        else:
            print("⚠️  Structure SW non reconnue — remplacement non effectué")
    else:
        print("⚠️  Bloc serviceWorker introuvable dans le fichier")

# ── 4. Écriture du fichier de destination ────────────────────────────────────
os.makedirs(os.path.dirname(DEST), exist_ok=True)
with open(DEST, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(DEST) // 1024
print(f"✅ index.html généré → {DEST} ({size_kb} Ko)")
print("Done.")
