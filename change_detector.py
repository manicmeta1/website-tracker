from difflib import SequenceMatcher
from typing import Dict, List, Any
import re
from screenshot_manager import ScreenshotManager
from change_scorer import ChangeScorer

class ChangeDetector:
    def __init__(self):
        self.previous_content = None
        self.screenshot_manager = ScreenshotManager()
        self.change_scorer = ChangeScorer()  # Add change scorer

    def detect_changes(self, current_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detects changes between current and previous content"""
        if not self.previous_content:
            self.previous_content = current_content
            return []

        changes = []

        # Check content hash for quick comparison
        if current_content['content_hash'] == self.previous_content['content_hash']:
            return []

        # Compare text content
        text_changes = self._compare_text(
            self.previous_content['text_content'],
            current_content['text_content'],
            current_content['timestamp']
        )
        if text_changes:
            changes.extend(text_changes)

        # Compare links
        link_changes = self._compare_links(
            self.previous_content['links'],
            current_content['links'],
            current_content['timestamp']
        )
        if link_changes:
            changes.extend(link_changes)

        # Compare styles
        style_changes = self._compare_styles(
            self.previous_content.get('styles', {}),
            current_content.get('styles', {}),
            current_content['timestamp']
        )
        if style_changes:
            changes.extend(style_changes)

        # Compare menu structure
        menu_changes = self._compare_menu_structure(
            self.previous_content.get('menu_structure', []),
            current_content.get('menu_structure', []),
            current_content['timestamp']
        )
        if menu_changes:
            changes.extend(menu_changes)

        # Compare screenshots
        if 'screenshot_path' in self.previous_content and 'screenshot_path' in current_content:
            try:
                before_img, after_img, diff_img = self.screenshot_manager.compare_screenshots(
                    self.previous_content['screenshot_path'],
                    current_content['screenshot_path']
                )
                changes.append({
                    'type': 'visual_change',
                    'location': 'Website Screenshot',
                    'before_image': before_img,
                    'after_image': after_img,
                    'diff_image': diff_img,
                    'timestamp': current_content['timestamp']
                })
            except Exception as e:
                print(f"Warning: Failed to compare screenshots: {str(e)}")

        # Update previous content
        self.previous_content = current_content

        # Score the changes using AI
        if changes:
            changes = self.change_scorer.score_changes(changes)

        return changes

    def _compare_text(self, old_text: str, new_text: str, timestamp: str) -> List[Dict[str, Any]]:
        """Compares text content and returns changes"""
        changes = []

        # Split into paragraphs
        old_paragraphs = re.split(r'\n\s*\n', old_text)
        new_paragraphs = re.split(r'\n\s*\n', new_text)

        for i, (old_p, new_p) in enumerate(zip(old_paragraphs, new_paragraphs)):
            if old_p != new_p:
                matcher = SequenceMatcher(None, old_p, new_p)
                if matcher.ratio() < 0.95:  # Threshold for significant changes
                    changes.append({
                        'type': 'text_change',
                        'location': f'Paragraph {i + 1}',
                        'before': old_p,
                        'after': new_p,
                        'timestamp': timestamp
                    })

        return changes

    def _compare_links(self, old_links: List[str], new_links: List[str], timestamp: str) -> List[Dict[str, Any]]:
        """Compares links and returns changes"""
        changes = []

        # Find added links
        added = set(new_links) - set(old_links)
        if added:
            changes.append({
                'type': 'links_added',
                'location': 'Links',
                'before': '',
                'after': '\n'.join(added),
                'timestamp': timestamp
            })

        # Find removed links
        removed = set(old_links) - set(new_links)
        if removed:
            changes.append({
                'type': 'links_removed',
                'location': 'Links',
                'before': '\n'.join(removed),
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