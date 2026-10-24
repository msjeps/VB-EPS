# VB EPS — TODO post-audit de sécurité (2026-10-24)

Source : `security-audit-reports/VB-EPS/REPORT.md` — 5 failles confirmées, 0 faux positif.

---

## ✅ Priorité 1 — Sécurité MEDIUM (CORRIGÉ le 2026-10-24)

### 1. ~~XSS stockée — échappement HTML manquant dans VB_EPS.html ET pwa-build/index.html~~

**Faille** : les données saisies par les élèves (prénom, nom, classe) sont injectées directement dans le DOM via `innerHTML` sans échappement, dans 5 fonctions :
- `buildResults()` (ligne ~1964)
- `buildJoueursFields()` (ligne ~1020)
- `buildHistoryUI()` (ligne ~2787)
- `showHistory()` (ligne ~2804)
- `buildExportScreen()` (ligne ~2066)

**Impact** : un élève peut injecter `<img src=x onerror=alert(...)>` — le payload s'exécute sur l'écran résultats et persiste en localStorage pour le prochain utilisateur de la tablette partagée.

**Correction** : ✅ Déjà appliquée — `escapeHtml()` présente et utilisée dans les 5 sinks dans VB_EPS.html ET pwa-build/index.html.

---

### 2. ~~Injection de formules dans l'export CSV~~ ✅ CORRIGÉ le 2026-10-24

**Faille** : les noms d'élèves commençant par `=`, `+`, `-`, `@` sont écrits tels quels dans le CSV exporté. Excel/LibreOffice/Sheets les interprètent comme des formules à l'ouverture du fichier.

**Impact** : le professeur ouvre l'export et voit des données modifiées ou des erreurs de formule — les notes peuvent être altérées silencieusement.

**Correction** : ✅ Appliquée — `csvField()` ajoutée (ligne ~3020/3024) et utilisée dans `getCSV()` (ligne ~2266/2270) dans VB_EPS.html ET pwa-build/index.html. Chaque valeur est entre guillemets doubles ; les valeurs commençant par `= + - @` sont préfixées d'une apostrophe.

---

## ✅ Priorité 2 — Sécurité MEDIUM (CORRIGÉ le 2026-10-24)

> Projet source Android recréé dans `android/` le 2026-10-24.

### 3. ~~WebView — accès universel aux fichiers activé~~ ✅ CORRIGÉ

**Faille** (bytecode vérifié dans le APK) : `setAllowUniversalAccessFromFileURLs(true)` + `setAllowFileAccessFromFileURLs(true)` — combiné avec la faille XSS (n°1), permet à un script de lire d'autres fichiers `file://` du processus.

**Correction** : ✅ Appliquée dans `android/app/src/main/java/com/eps/vbeps/MainActivity.java` :
- `setAllowUniversalAccessFromFileURLs(false)` + `setAllowFileAccessFromFileURLs(false)` explicites
- `WebViewClient` avec `shouldOverrideUrlLoading` limité à `file:///android_asset/`
- Bonus : `AndroidDownload` interface ajoutée pour remplacer blob: URL (non géré par WebView)
- `downloadCSV()` mis à jour dans VB_EPS.html et pwa-build/index.html

---

## ✅ Priorité 3 — Sécurité LOW (CORRIGÉ le 2026-10-24)

### 4. ~~android:allowBackup="true" dans l'APK~~ ✅ CORRIGÉ

**Correction** : ✅ `android:allowBackup="false"` dans `android/app/src/main/AndroidManifest.xml`

---

### 5. Mot de passe admin en clair

**Faille** : `'ADMINPROF'` en clair dans `checkAdmin()` (ligne ~2856) — lisible par tout élève via "Voir le code source".

**Impact limité** : ne donne accès qu'aux réglages barèmes/export/chrono, pas aux données.

**Correction** : comparer un hash SHA-256 côté client, comme LaserFit (`checkPassword()` avec `crypto.subtle.digest`). Documenter que cela élève la barre sans être une protection absolue (devtools toujours possible).

---

## 🔵 Priorité 4 — Hygiène et documentation

### 6. Supprimer VB_EPS.html.bak

Fichier résidu inutile à la racine du projet. Aucun risque sécurité (pas servi), mais pollution du dépôt.

```bash
rm "/Users/nathalieprenois/AndroidStudioProjects/VB EPS/VB_EPS.html.bak"
```

---

### 7. Mettre à jour CLAUDE.md (dérives documentaires)

Le CLAUDE.md actuel contient des inexactitudes signalées par l'audit :
- [ ] "pas de wrapper APK, PWA native" → faux : `VB_EPS_signed.apk` existe (com.eps.vbeps), projet source absent
- [ ] "Persistance : localStorage + IndexedDB" → faux : **localStorage uniquement** (IndexedDB absent de VB_EPS.html)
- [ ] "Wake Lock API" dans conventions communes → **absent** de VB_EPS.html actuellement (à ajouter si besoin)
- [ ] Mettre à jour la section Sécurité pour refléter les 5 failles et leurs corrections

---

## 🚀 Priorité 5 — Infrastructure (Release GitHub + dossier de distribution)

### 8. ~~Créer le projet source Android (wrapper WebView VB EPS)~~ ✅ FAIT le 2026-10-24

Projet créé dans `android/` (convention Match Manager EPS / SCAN EPS) :
- Package : `com.eps.vbeps`, tâche `syncWebApp` (copie `pwa-build/` → `assets/`)
- Toutes les corrections sécurité appliquées (findings 3 et 4)
- `vbeps.jks` existante réutilisée (`/Users/nathalieprenois/AndroidStudioProjects/vbeps.jks`)
- ⚠️ **À faire** : copier `keystore.properties.template` → `keystore.properties` et remplir les mots de passe

---

### 9. Créer la Release GitHub et mettre en place la structure de distribution

Quand l'APK est prête (après corrections n°3 et n°4) :

**a) Dépôt GitHub**
- Vérifier que le dépôt `msjeps/VB-EPS` existe (ou le créer)
- S'assurer que le `.gitignore` exclut : `*.jks`, `keystore.properties`, `*.apk`, `build/`, `.DS_Store`, `CLAUDE.md`
- Créer la Release : `gh release create v3.0 VB_EPS.apk --title "VB EPS v3.0" --notes "..."`
- Lien de téléchargement : `https://github.com/msjeps/VB-EPS/releases/latest/download/VB_EPS.apk`

**b) Dossier de distribution local (clone de référence)**
```
~/Documents/APPLI EPS/APPLI EPS/Vb eps/   ← clone du dépôt public msjeps/VB-EPS
    ├── (clone git — index.html, sw.js, manifest.json, etc.)
    ├── VB_EPS.apk                          ← copie de l'APK publié (ignoré par git)
    └── Vb-eps-backup/                      ← anciens APK + clé .jks (ignoré par git)
```

Commandes à lancer **depuis un autre répertoire** (cf. piège `Documents/APPLI EPS` en session) :
```bash
cd /tmp
git clone https://github.com/msjeps/VB-EPS.git "/Users/nathalieprenois/Documents/APPLI EPS/APPLI EPS/Vb eps"
```

Puis copier l'APK publié :
```bash
cp "/Users/nathalieprenois/AndroidStudioProjects/VB EPS/android/app/build/outputs/apk/release/VB_EPS.apk" \
   "/Users/nathalieprenois/Documents/APPLI EPS/APPLI EPS/Vb eps/VB_EPS.apk"
```

**c) Après chaque publication future**
- `git -C "/Users/nathalieprenois/Documents/APPLI EPS/APPLI EPS/Vb eps" pull`
- Copier l'APK publié
- Vérifier `git status` propre + `cmp index.html` identique à la copie de travail

---

## Récapitulatif des fichiers à modifier

| Fichier | Tâches concernées |
|---------|------------------|
| `VB_EPS.html` | 1 (XSS ×5 sinks), 2 (CSV injection), 5 (mot de passe) |
| `pwa-build/index.html` | 1 (XSS ×5 sinks), 2 (CSV injection) — sync avec VB_EPS.html |
| `android/app/.../MainActivity.kt` | 3 (WebView flags) — projet à créer |
| `android/app/src/main/AndroidManifest.xml` | 4 (allowBackup) — projet à créer |
| `CLAUDE.md` | 7 (dérives documentaires) |

---

*Généré le 2026-10-24 à partir du rapport `security-audit-skill/VB-EPS/run-1/REPORT.md`*
