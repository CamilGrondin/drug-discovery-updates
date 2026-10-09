# HelixGrid - Serveur de Mises à Jour (Tauri v2)

Ce dépôt héberge le registre et les annonces de mise à jour automatique pour le client lourd **HelixGrid** (application de calcul distribué pour le criblage de molécules).

---

## 📡 Comment fonctionne l'Auto-Update ?

1. **Vérification automatique :**
   Lors du démarrage de l'application cliente ou via son interface, le client interroge ce dépôt via :
   - `https://raw.githubusercontent.com/CamilGrondin/helixgrid-updates/main/latest.json`
   - `https://github.com/CamilGrondin/helixgrid-updates/releases/latest/download/latest.json`

2. **Comparaison de version & Annonce :**
   Le client compare sa version actuelle (ex: `0.1.0`) avec celle déclarée dans `latest.json`.
   - Si une version plus récente est disponible (ex: `0.3.0`), une **bannière visuelle** s'affiche dans l'application avec les notes de version (changelog) et le bouton **« Mettre à jour maintenant »**.
   - Des logs sont également affichés dans la console de calcul.

3. **Téléchargement sécurisé & Signature :**
   Le client télécharge l'archive correspondant à son OS/architecture (`darwin-aarch64`, `darwin-x86_64`, `windows-x86_64`, `linux-x86_64`).
   L'intégrité et l'authenticité sont vérifiées grâce à la signature cryptographique Ed25519 (Minisign) associée à la clé publique de l'application.

4. **Installation & Redémarrage :**
   La mise à jour est appliquée à chaud et l'application redémarre instantanément dans la nouvelle version.

---

## 🔑 Sécurité & Clés Cryptographiques

- **Clé publique intégrée dans `tauri.conf.json`** :
  ```text
  dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHB1YmxpYyBrZXk6IDFDRjFFQUU0NDUzNEVDNEQKUldSTjdEUkY1T3J4SENUTkd0K1B0MnlYUko5OS9DaWY3aXJBYkdYUTM3TWZiQThvMlNVVmc2LzMK
  ```
- **Clé privée (`updater.key`)** :
  Conservée localement dans `helixgrid-ui/src-tauri/updater.key` (ignorée par Git). **Ne jamais la partager ni la committer sur un dépôt public !**

---

## 🚀 Comment annoncer une nouvelle version aux clients ?

### Option 1 : Utiliser le script `publish_release.py` (Recommandé)

Pour mettre à jour le manifest et pousser l'annonce sur GitHub :

```bash
python3 publish_release.py --version 0.3.0 --notes "Mise à jour majeure : HelixGrid Rebranding & multi-cibles" --commit
```

### Option 2 : Modifier manuellement `latest.json`

Éditez `latest.json` :

```json
{
  "version": "0.3.0",
  "notes": "Description des nouveautés et correctifs...",
  "pub_date": "2026-10-09T12:00:00Z",
  "platforms": {
    "darwin-aarch64": {
      "signature": "<signature_générée_par_tauri_signer>",
      "url": "https://github.com/CamilGrondin/helixgrid-updates/releases/download/v0.3.0/HelixGrid_0.3.0_aarch64.app.tar.gz"
    }
  }
}
```

Puis committez et poussez :
```bash
git add latest.json
git commit -m "release: annonce de la version 0.3.0"
git push origin main
```

Dès le push effectué, tous les clients connectés recevront l'alerte de mise à jour lors de leur prochain lancement !

---

## 🛠️ Générer et signer les binaires avec Tauri CLI

Pour compiler et générer les archives d'update :
```bash
export TAURI_SIGNING_PRIVATE_KEY="$(cat ../helixgrid-ui/src-tauri/updater.key)"
npm run tauri build
```
Les bundles signés et leurs fichiers `.sig` seront générés dans `src-tauri/target/release/bundle/`.
