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

### 6. ~~Supprimer VB_EPS.html.bak~~ ✅ FAIT le 2026-10-24

---

### 7. ~~Mettre à jour CLAUDE.md (dérives documentaires)~~ ✅ FAIT le 2026-10-24

Corrections appliquées :
- Structure : projet `android/` documenté, anciens APK binaires signalés comme reliques
- Persistance : localStorage uniquement (IndexedDB absent confirmé)
- Wake Lock : marqué absent, à ajouter si besoin
- Section Sécurité : XSS, CSV injection, APK WebView flags, mot de passe admin tous documentés

---

## 🚀 Priorité 5 — Infrastructure (Release GitHub + dossier de distribution)

### 8. ~~Créer le projet source Android (wrapper WebView VB EPS)~~ ✅ FAIT le 2026-10-24

Projet créé dans `android/` : package `com.eps.vbeps`, tâche `syncWebApp`, `vbeps.jks` réutilisée.

---

### 9. ~~Créer la Release GitHub et mettre en place la structure de distribution~~ ✅ FAIT le 2026-10-24

- Release `v3.0` publiée sur `msjeps/VB-EPS`
- Lien APK : `https://github.com/msjeps/VB-EPS/releases/latest/download/VB_EPS.apk`
- Clone de référence initialisé dans `~/Documents/APPLI EPS/APPLI EPS/Vb eps/`, APK copié, git status propre

**Après chaque publication future** :
```bash
git --git-dir="/Users/nathalieprenois/Documents/APPLI EPS/APPLI EPS/Vb eps/.git" \
    --work-tree="/Users/nathalieprenois/Documents/APPLI EPS/APPLI EPS/Vb eps" pull
# puis copier l'APK publié dans ce dossier
```
Note : `cd` + `ls` dans `Documents/APPLI EPS` → "Operation not permitted" dans cette session ; utiliser `--git-dir` + `--work-tree`.

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
