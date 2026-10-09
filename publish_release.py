#!/usr/bin/env python3
"""
publish_release.py - Script pour annoncer et publier une mise à jour Tauri

Ce script permet de :
1. Mettre à jour le fichier `latest.json` avec la nouvelle version, les notes de version et la date.
2. Signer cryptographiquement les binaires (.tar.gz, .zip, .AppImage) à l'aide de la clé privée Tauri.
3. Optionnellement pousser les changements sur GitHub et créer une GitHub Release.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

DEFAULT_KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../drug-discovery-ui/src-tauri/updater.key"))
LATEST_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "latest.json"))

def sign_file(file_path: str, key_path: str, password: str = "") -> str:
    """Signe un fichier binaire avec tauri signer et retourne la signature."""
    if not os.path.exists(file_path):
        print(f"[-] Fichier introuvable : {file_path}")
        sys.exit(1)
    
    if not os.path.exists(key_path):
        print(f"[-] Clé privée introuvable : {key_path}")
        sys.exit(1)

    print(f"[*] Signature de {file_path} avec {key_path}...")
    cmd = [
        "npx", "@tauri-apps/cli", "signer", "sign",
        "-f", key_path,
        "-p", password,
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Erreur de signature : {result.stderr}")
        sys.exit(1)

    sig_file = f"{file_path}.sig"
    if os.path.exists(sig_file):
        with open(sig_file, "r") as f:
            return f.read().strip()
    
    # Extraire depuis la sortie standard si .sig n'est pas trouvé
    for line in result.stdout.splitlines():
        if len(line) > 60 and not line.startswith("Public") and not line.startswith("Your"):
            return line.strip()
    
    raise RuntimeError("Impossible de récupérer la signature générée.")

def update_manifest(version: str, notes: str, platforms_data: dict, output_path: str = LATEST_JSON_PATH):
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "version": version,
        "notes": notes,
        "pub_date": now_iso,
        "platforms": platforms_data
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[+] Manifest {output_path} mis à jour avec succès pour la version {version} !")
    return manifest

def main():
    parser = argparse.ArgumentParser(description="Publier une mise à jour pour drug-discovery-ui")
    parser.add_argument("--version", "-v", required=True, help="Nouvelle version (ex: 0.2.0)")
    parser.add_argument("--notes", "-n", default="Nouvelle version avec améliorations et correctifs.", help="Notes de version")
    parser.add_argument("--key", "-k", default=DEFAULT_KEY_PATH, help="Chemin vers la clé privée updater.key")
    parser.add_argument("--key-password", default="", help="Mot de passe de la clé privée")
    parser.add_argument("--commit", action="store_true", help="Commit et push automatique sur le repo GitHub")
    args = parser.parse_args()

    # Charger le manifest existant s'il existe pour conserver la structure des plateformes
    platforms = {}
    if os.path.exists(LATEST_JSON_PATH):
        try:
            with open(LATEST_JSON_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
                platforms = existing.get("platforms", {})
        except Exception:
            pass

    # Mettre à jour les URLs de téléchargement avec la nouvelle version
    for platform_key in list(platforms.keys()):
        old_url = platforms[platform_key].get("url", "")
        if "/releases/download/" in old_url:
            # Remplacer le tag vX.Y.Z et le nom de version dans l'URL
            parts = old_url.split("/releases/download/")
            base = parts[0]
            filename = parts[1].split("/", 1)[1] if "/" in parts[1] else parts[1]
            # Mettre à jour le nom de fichier si la version y apparaît
            new_filename = filename.replace(existing.get("version", ""), args.version)
            platforms[platform_key]["url"] = f"{base}/releases/download/v{args.version}/{new_filename}"

    manifest = update_manifest(args.version, args.notes, platforms)
    print("\nNouveau manifest :")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

    if args.commit:
        print("\n[*] Commit et push des modifications...")
        subprocess.run(["git", "add", "latest.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"release: v{args.version}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[+] Modifications poussées sur GitHub !")

if __name__ == "__main__":
    main()
