#!/usr/bin/env python3

import logging
import sys
import os
import requests
from itertools import groupby

# --- Grundkonfiguration des Loggings ---
logging.basicConfig(
  stream=sys.stdout,
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Immich:
    def __init__(self, api_url: str, key: str):
        # Die URL wird genau so verwendet, wie sie übergeben wird.
        self.api_url = api_url.rstrip('/')
        self.headers = {
          'x-api-key': key,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
        logger.info(f"Immich-Client initialisiert für URL: {self.api_url}")

    def get_all_assets(self):
        logger.info('⬇️  Alle Assets werden abgerufen (dies kann bei großen Bibliotheken eine Weile dauern)...')

        all_assets = []
        page = 1

        while True:
            try:
                # Wir verwenden /search/metadata, da dies der dokumentierte Weg ist, um Assets aufzulisten.
                payload = {"page": page, "size": 1000}
                response = requests.post(f"{self.api_url}/search/metadata", headers=self.headers, json=payload, timeout=60)
                response.raise_for_status()

                data = response.json()
                assets_on_page = data.get('assets', {}).get('items', [])

                if not assets_on_page:
                    # Keine weiteren Assets gefunden, Schleife beenden.
                    break

                all_assets.extend(assets_on_page)
                logger.info(f"   {len(all_assets)} Assets bisher abgerufen...")

                # Überprüfen, ob es eine nächste Seite gibt
                if not data.get('assets', {}).get('nextPage'):
                    break

                page += 1

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    logger.error("❌ Fehler beim Abrufen der Assets: Der API-Schlüssel ist ungültig.")
                else:
                    logger.error(f"❌ Fehler beim Abrufen der Assets: HTTP-Fehler: {e.response.status_code}")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Fehler beim Abrufen der Assets: Verbindungsfehler: {e}")
                return None

        logger.info(f"✅ Insgesamt {len(all_assets)} Assets abgerufen.")
        return all_assets

    def get_all_tags(self):
        try:
            response = requests.get(f"{self.api_url}/tags", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen der Tags: {e}")
            return None

    def create_tag(self, tag_name):
        logger.info(f"Tag '{tag_name}' wird erstellt...")
        response = None
        try:
            # Annahme: Der Endpunkt zum Erstellen von Tags hat sich nicht geändert.
            payload = {'name': tag_name, 'type': 'OBJECT'}
            response = requests.post(f"{self.api_url}/tags", headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Tag '{tag_name}' erfolgreich erstellt.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Erstellen des Tags '{tag_name}': {e}")
            if response is not None and "duplicate key" in response.text:
                 logger.info(f"Tag '{tag_name}' existiert bereits.")
                 return self.get_tag_by_name(tag_name)
            return None

    def get_tag_by_name(self, tag_name):
        all_tags = self.get_all_tags()
        if all_tags:
            for tag in all_tags:
                if tag['name'] == tag_name:
                    return tag
        return None

    def tag_assets(self, tag_id, asset_ids):
        logger.info(f"{len(asset_ids)} Assets werden getaggt...")
        try:
            # Annahme: Der Endpunkt zum Taggen von Assets hat sich nicht geändert.
            payload = {"ids": asset_ids}
            response = requests.put(f"{self.api_url}/tags/{tag_id}/assets", headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"{len(asset_ids)} Assets erfolgreich getaggt.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Taggen der Assets: {e}")
            return None

def find_duplicate_videos(assets):
    logger.info("Suche nach doppelten Videos...")

    def get_base_filename(asset):
        return os.path.splitext(asset['originalFileName'])[0]

    assets.sort(key=get_base_filename)
    grouped_assets = groupby(assets, key=get_base_filename)
    video_ids_to_tag = []

    for _, group_iter in grouped_assets:
        group = list(group_iter)
        if len(group) > 1:
            has_jpg = any(item['originalFileName'].lower().endswith(('.jpg', '.jpeg')) for item in group)
            if has_jpg:
                for item in group:
                    if item['originalFileName'].lower().endswith('.mp4'):
                        video_ids_to_tag.append(item['id'])

    logger.info(f"{len(video_ids_to_tag)} Videos zum Taggen gefunden.")
    return video_ids_to_tag

def main():
    api_key = os.environ.get("IMMICH_API_KEY")
    api_url = os.environ.get("IMMICH_API_URL")
    tag_name = "Duplicate Video From Google Photos"

    if not api_key or not api_url:
        logger.error("Die Umgebungsvariablen IMMICH_API_KEY und IMMICH_API_URL sind erforderlich.")
        logger.info("Beispiel: export IMMICH_API_URL='http://192.168.178.28:2283/api'")
        return

    immich = Immich(api_url, api_key)

    assets = immich.get_all_assets()
    if not assets:
        logger.error("Skript wird beendet, da keine Assets abgerufen werden konnten.")
        return

    video_ids_to_tag = find_duplicate_videos(assets)
    if not video_ids_to_tag:
        logger.info("Keine doppelten Videos zum Taggen gefunden.")
        return

    tag = immich.get_tag_by_name(tag_name)
    if not tag:
        tag = immich.create_tag(tag_name)
    if not tag:
        logger.error(f"Konnte den Tag '{tag_name}' nicht finden oder erstellen. Abbruch.")
        return

    tag_id = tag['id']
    immich.tag_assets(tag_id, video_ids_to_tag)

    logger.info("Skript erfolgreich abgeschlossen.")

if __name__ == '__main__':
    main()
