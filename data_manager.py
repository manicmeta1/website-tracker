import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class DataManager:
    def __init__(self):
        self.changes_file = "changes.json"
        self.config_file = "website_config.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create necessary files if they don't exist"""
        for file_path in [self.changes_file, self.config_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def store_website_config(self, website: Dict[str, Any]):
        """Store website configuration"""
        try:
            configs = self.get_website_configs()

            # Update existing or add new
            existing = next((w for w in configs if w['url'] == website['url']), None)
            if existing:
                configs.remove(existing)
            configs.append(website)

            with open(self.config_file, 'w') as f:
                json.dump(configs, f, indent=2)

        except Exception as e:
            raise Exception(f"Failed to store website config: {str(e)}")

    def get_website_configs(self) -> List[Dict[str, Any]]:
        """Get all website configurations"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def delete_website_config(self, url: str):
        """Delete website configuration"""
        configs = self.get_website_configs()
        configs = [w for w in configs if w['url'] != url]
        with open(self.config_file, 'w') as f:
            json.dump(configs, f, indent=2)

    def store_changes(self, changes: List[Dict[str, Any]], url: str):
        """Store detected changes for a specific website"""
        try:
            print(f"Storing changes for {url}: {len(changes)} changes")
            with open(self.changes_file, 'r') as f:
                existing_changes = json.load(f)

            # Add website URL and timestamp to changes
            for change in changes:
                change['url'] = url
                change['timestamp'] = datetime.now().isoformat()

                # Store pages data
                if 'pages' in change:
                    # Extract only necessary page information
                    change['monitored_pages'] = [
                        {'url': page['url'], 'location': page.get('location', 'Unknown')}
                        for page in change.get('pages', [])
                        if isinstance(page, dict)
                    ]
                    print(f"Stored {len(change['monitored_pages'])} monitored pages for {url}")

                existing_changes.append(change)

            # Keep only last 100 changes per website
            url_changes = {}
            for change in reversed(existing_changes):
                change_url = change['url']
                if change_url not in url_changes:
                    url_changes[change_url] = []
                if len(url_changes[change_url]) < 100:
                    url_changes[change_url].append(change)

            # Flatten the changes
            all_changes = []
            for url_change_list in url_changes.values():
                all_changes.extend(url_change_list)

            with open(self.changes_file, 'w') as f:
                json.dump(all_changes, f, indent=2)

            print(f"Successfully stored changes for {url}")

        except Exception as e:
            print(f"Error storing changes: {str(e)}")
            raise Exception(f"Failed to store changes: {str(e)}")

    def get_recent_changes(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve recent changes, optionally filtered by URL"""
        try:
            print(f"Loading changes from {self.changes_file}")  # Debug log
            with open(self.changes_file, 'r') as f:
                changes = json.load(f)
                print(f"Loaded {len(changes)} changes")  # Debug log

            if url:
                changes = [c for c in changes if c['url'] == url]
                print(f"Retrieved {len(changes)} changes for {url}")
            else:
                print(f"Retrieved {len(changes)} total changes")

            return changes[-100:]  # Return last 100 changes

        except Exception as e:
            print(f"Error retrieving changes: {str(e)}")
            return []