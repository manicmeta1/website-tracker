import hashlib
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Dict, List, Any
from screenshot_manager import ScreenshotManager
from change_scorer import ChangeScorer

class ChangeDetector:
    def __init__(self):
        self.previous_content = None
        self.screenshot_manager = ScreenshotManager()
        self.change_scorer = ChangeScorer()

    def detect_changes(self, current_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detects changes between current and previous content"""
        # Ensure we have a timestamp
        if 'timestamp' not in current_content:
            current_content['timestamp'] = datetime.now(timezone.utc).isoformat()

        # Map text to text_content if needed
        if 'text' in current_content and 'text_content' not in current_content:
            current_content['text_content'] = current_content['text']

        # Generate content hash if not present
        if 'content_hash' not in current_content:
            current_content['content_hash'] = self._generate_content_hash(current_content)

        # Handle first run case
        if not self.previous_content:
            self.previous_content = current_content
            return [{
                'type': 'site_check',
                'location': 'Initial Check',
                'timestamp': current_content['timestamp'],
                'pages': current_content.get('pages', [])
            }]

        # Map text to text_content in previous content if needed
        if 'text' in self.previous_content and 'text_content' not in self.previous_content:
            self.previous_content['text_content'] = self.previous_content['text']

        changes = []

        # Compare pages
        page_changes = self._compare_pages(
            self.previous_content.get('pages', []),
            current_content.get('pages', []),
            current_content['timestamp']
        )
        changes.extend(page_changes)

        # Compare text content
        text_changes = self._compare_text(
            self.previous_content.get('text_content', ''),
            current_content.get('text_content', ''),
            current_content['timestamp']
        )
        changes.extend(text_changes)

        # Update previous content
        self.previous_content = current_content

        # Score and return changes
        if changes:
            changes = self.change_scorer.score_changes(changes)
            return changes
        else:
            # If no changes detected, return site check
            return [{
                'type': 'site_check',
                'location': 'Site Check',
                'timestamp': current_content['timestamp'],
                'pages': current_content.get('pages', [])
            }]

    def _generate_content_hash(self, content: Dict[str, Any]) -> str:
        """Generate a hash of the content for quick comparison"""
        content_str = str(content.get('text_content', ''))
        content_str += str(content.get('pages', []))
        return hashlib.md5(content_str.encode()).hexdigest()

    def _compare_text(self, old_text: str, new_text: str, timestamp: str) -> List[Dict[str, Any]]:
        """Compares text content and returns changes"""
        changes = []

        if old_text != new_text:
            changes.append({
                'type': 'text_change',
                'location': 'Content',
                'before': old_text,
                'after': new_text,
                'timestamp': timestamp
            })

        return changes

    def _compare_pages(self, old_pages: List[Dict[str, str]], new_pages: List[Dict[str, str]], 
                      timestamp: str) -> List[Dict[str, Any]]:
        """Compare page structures and detect additions/removals"""
        changes = []

        # Convert pages to sets for comparison
        old_urls = {p['url'] for p in old_pages}
        new_urls = {p['url'] for p in new_pages}

        # Find added pages
        added_urls = new_urls - old_urls
        if added_urls:
            added_pages = [p for p in new_pages if p['url'] in added_urls]
            for page in added_pages:
                changes.append({
                    'type': 'page_added',
                    'location': page['location'],
                    'timestamp': timestamp,
                    'url': page['url']
                })

        # Find removed pages
        removed_urls = old_urls - new_urls
        if removed_urls:
            removed_pages = [p for p in old_pages if p['url'] in removed_urls]
            for page in removed_pages:
                changes.append({
                    'type': 'page_removed',
                    'location': page['location'],
                    'timestamp': timestamp,
                    'url': page['url']
                })

        return changes

    def _compare_links(self, old_links: List[str], new_links: List[str], timestamp: str) -> List[Dict[str, Any]]:
        """Compares links and returns changes"""
        changes = []

        # Convert lists to sets for easier comparison
        old_set = set(old_links)
        new_set = set(new_links)

        # Find added links
        added = new_set - old_set
        if added:
            changes.append({
                'type': 'links_added',
                'location': 'Links',
                'before': '',
                'after': '\n'.join(sorted(added)),
                'timestamp': timestamp
            })

        # Find removed links
        removed = old_set - new_set
        if removed:
            changes.append({
                'type': 'links_removed',
                'location': 'Links',
                'before': '\n'.join(sorted(removed)),
                'after': '',
                'timestamp': timestamp
            })

        return changes

    def _compare_styles(self, old_styles: Dict[str, Any], new_styles: Dict[str, Any], timestamp: str) -> List[Dict[str, Any]]:
        """Compares style changes (fonts, text sizes, colors)"""
        changes = []

        for style_type in ['fonts', 'text_sizes', 'colors']:
            old_values = set(old_styles.get(style_type, []))
            new_values = set(new_styles.get(style_type, []))

            # Added styles
            added = new_values - old_values
            if added:
                changes.append({
                    'type': f'{style_type}_added',
                    'location': f'Style - {style_type}',
                    'before': '',
                    'after': '\n'.join(sorted(added)),
                    'timestamp': timestamp
                })

            # Removed styles
            removed = old_values - new_values
            if removed:
                changes.append({
                    'type': f'{style_type}_removed',
                    'location': f'Style - {style_type}',
                    'before': '\n'.join(sorted(removed)),
                    'after': '',
                    'timestamp': timestamp
                })

        return changes

    def _compare_menu_structure(self, old_menu: List[Dict[str, str]], new_menu: List[Dict[str, str]], timestamp: str) -> List[Dict[str, Any]]:
        """Compares navigation menu structure"""
        changes = []

        if old_menu != new_menu:
            # Get first menu from each list (if exists)
            old_menu_items = old_menu[0] if old_menu else []
            new_menu_items = new_menu[0] if new_menu else []

            # Convert menu structures to readable format
            def format_menu(menu_items):
                return '\n'.join([
                    f"- {item.get('text', '')} ({item.get('href', '')})"
                    for item in menu_items
                ])

            changes.append({
                'type': 'menu_structure_change',
                'location': 'Navigation Menu',
                'before': format_menu(old_menu_items),
                'after': format_menu(new_menu_items),
                'timestamp': timestamp
            })

        return changes