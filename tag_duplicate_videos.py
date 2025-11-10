#!/usr/bin/env python3

import logging
import sys
import os
import requests
from itertools import groupby

logging.basicConfig(
  stream=sys.stdout,
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from urllib.parse import urlparse

class Immich:
    def __init__(self, url: str, key: str):
        self.api_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}/api'
        self.headers = {
          'x-api-key': key,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }

    def get_all_assets(self):
        logger.info(f'⬇️  Fetching all assets... This may take a while for large libraries.')
        try:
            response = requests.get(f"{self.api_url}/assets", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching assets: {e}")
            return None

    def get_all_tags(self):
        try:
            response = requests.get(f"{self.api_url}/tags", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tags: {e}")
            return None

    def create_tag(self, tag_name):
        logger.info(f"Creating tag '{tag_name}'...")
        response = None
        try:
            payload = {'name': tag_name, 'type': 'OBJECT'}
            response = requests.post(f"{self.api_url}/tags", headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Tag '{tag_name}' created successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating tag '{tag_name}': {e}")
            if response is not None and "duplicate key" in response.text:
                 logger.info(f"Tag '{tag_name}' already exists.")
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
        logger.info(f"Tagging {len(asset_ids)} assets...")
        try:
            payload = {"ids": asset_ids}
            response = requests.put(f"{self.api_url}/tags/{tag_id}/assets", headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully tagged {len(asset_ids)} assets.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error tagging assets: {e}")
            return None

def find_duplicate_videos(assets):
    logger.info("Finding duplicate videos...")

    def get_base_filename(asset):
        return os.path.splitext(asset['originalFileName'])[0]

    assets.sort(key=get_base_filename)

    grouped_assets = groupby(assets, key=get_base_filename)

    video_ids_to_tag = []

    for base_filename, group_iter in grouped_assets:
        group = list(group_iter)
        if len(group) > 1:
            has_jpg = any(item['originalFileName'].lower().endswith(('.jpg', '.jpeg')) for item in group)

            if has_jpg:
                for item in group:
                    if item['originalFileName'].lower().endswith('.mp4'):
                        video_ids_to_tag.append(item['id'])

    logger.info(f"Found {len(video_ids_to_tag)} videos to tag.")
    return video_ids_to_tag

def main():
    api_key = os.environ.get("IMMICH_API_KEY")
    api_url = os.environ.get("IMMICH_API_URL")
    tag_name = "Duplicate Video From Google Photos"

    if not api_key or not api_url:
        logger.error("IMMICH_API_KEY and IMMICH_API_URL environment variables are required")
        logger.info("Example: export IMMICH_API_KEY='your_api_key_here'")
        logger.info("Example: export IMMICH_API_URL='http://your-immich-instance:2283'")
        return

    immich = Immich(api_url, api_key)

    assets = immich.get_all_assets()
    if assets is None:
        return

    video_ids_to_tag = find_duplicate_videos(assets)

    if not video_ids_to_tag:
        logger.info("No duplicate videos found to tag.")
        return

    tag = immich.get_tag_by_name(tag_name)
    if not tag:
        tag = immich.create_tag(tag_name)

    if not tag:
        logger.error(f"Could not find or create tag '{tag_name}'. Exiting.")
        return

    tag_id = tag['id']

    immich.tag_assets(tag_id, video_ids_to_tag)

    logger.info("Script finished successfully.")

if __name__ == '__main__':
    main()
