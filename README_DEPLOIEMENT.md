# VB EPS — Guide de déploiement PWA

## Contenu du dossier

```
pwa-build/
├── index.html           ← Application principale (~1,6 Mo, tout embarqué)
├── manifest.json        ← Manifeste PWA (icônes, nom, couleurs, raccourcis)
├── sw.js                ← Service Worker (cache offline, mise à jour auto)
├── icon_192.png         ← Icône 192×192 (écran d'accueil Android/iOS)
├── icon_512.png         ← Icône 512×512 (écran accueil + app stores)
├── screenshots/         ← Captures à ajouter pour PWA Builder (app stores)
│   ├── screen_accueil.png   (à créer : 1080×1920 ou 1280×800)
│   └── screen_obs.png       (à créer : 1080×1920 ou 1280×800)
└── README_DEPLOIEMENT.md
```

---

## Option 1 — GitHub Pages (recommandé, gratuit)

### Étapes

1. **Créer un dépôt GitHub** (ex: `vb-eps`)
2. **Uploader tous les fichiers** du dossier `pwa-build/` à la racine du dépôt
3. **Activer GitHub Pages** :
   `Settings → Pages → Source : Deploy from branch → main → / (root) → Save`
4. L'URL sera : `https://[votre-pseudo].github.io/vb-eps/`

### Installation sur tablette (Android)

1. Ouvrir l'URL dans **Chrome**
2. Menu ⋮ → **"Ajouter à l'écran d'accueil"**
   ou attendre la bannière d'installation automatique
3. L'app s'installe comme une appli native ✅

### Installation sur iPad

1. Ouvrir l'URL dans **Safari**
2. Bouton partage → **"Sur l'écran d'accueil"**
3. Confirmer → L'app s'installe ✅

---

## Option 2 — PWA Builder (soumission App Stores)

[PWA Builder](https://www.pwabuilder.com/) permet de soumettre la PWA sur :
- **Google Play Store** (Android)
- **Microsoft Store** (Windows)
- **Apple App Store** (iOS — nécessite un compte développeur Apple)

### Étapes

1. Déployer d'abord sur GitHub Pages (Option 1)
2. Aller sur **https://www.pwabuilder.com/**
3. Entrer l'URL de GitHub Pages → **Start**
4. Vérifier que le score PWA est vert (manifest ✅ / SW ✅ / HTTPS ✅)
5. Choisir la plateforme cible et télécharger le package

### Screenshots pour les stores

PWA Builder demande des captures d'écran pour les stores.
Créer 2 captures dans `screenshots/` :
- **Mobile** : 1080×1920 px (portrait)
- **Desktop/tablette** : 1280×800 px (paysage)

Nommer les fichiers :
- `screenshots/screen_accueil.png`
- `screenshots/screen_obs.png`

---

## Option 3 — Hébergement local sur réseau WiFi

Pour utiliser sans internet **depuis le gymnase** via un routeur WiFi local :

```bash
# Sur un ordinateur Mac/Linux connecté au même WiFi
cd pwa-build/
python3 -m http.server 8080
# Accès depuis les tablettes : http://[IP-ordinateur]:8080
```

> ⚠️ Le Service Worker ne fonctionne qu'en HTTPS ou sur localhost.
> Pour l'option locale, utiliser directement `index.html` sur la tablette
> (mode fichier, sans SW — l'app fonctionne quand même via localStorage).

---

## Mise à jour de l'application

1. Régénérer `index.html` depuis le projet source :
   ```bash
   cd "VB EPS/"
   python3 build_pwa.py
   ```
2. Uploader le nouveau `pwa-build/index.html` sur GitHub
3. Incrémenter la version dans `sw.js` si besoin (`CACHE_NAME = 'vb-eps-v3'`)

---

## Barèmes personnalisés

Les barèmes modifiés via "Configuration avancée" (mot de passe : `ADMINPROF`)
sont **locaux à chaque tablette** (stockés dans localStorage).

Pour partager des barèmes modifiés sur toutes les tablettes :
mettre à jour `DEF_BAREME` dans le code source, régénérer, et redistribuer.
