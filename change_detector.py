from difflib import SequenceMatcher
from typing import Dict, List, Any
import re

class ChangeDetector:
    def __init__(self):
        self.previous_content = None
        
    def detect_changes(self, current_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detects changes between current and previous content
        """
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
            current_content['text_content']
        )
        if text_changes:
            changes.extend(text_changes)
            
        # Compare links
        link_changes = self._compare_links(
            self.previous_content['links'],
            current_content['links']
        )
        if link_changes:
            changes.extend(link_changes)
            
        # Update previous content
        self.previous_content = current_content
        
        return changes
        
    def _compare_text(self, old_text: str, new_text: str) -> List[Dict[str, Any]]:
        """
        Compares text content and returns changes
        """
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
                        'timestamp': current_content['timestamp']
                    })
                    
        return changes
        
    def _compare_links(self, old_links: List[str], new_links: List[str]) -> List[Dict[str, Any]]:
        """
        Compares links and returns changes
        """
        changes = []
        
        # Find added links
        added = set(new_links) - set(old_links)
        if added:
            changes.append({
                'type': 'links_added',
                'location': 'Links',
                'before': '',
                'after': '\n'.join(added),
                'timestamp': current_content['timestamp']
            })
            
        # Find removed links
        removed = set(old_links) - set(new_links)
        if removed:
            changes.append({
                'type': 'links_removed',
                'location': 'Links',
                'before': '\n'.join(removed),
                'after': '',
                'timestamp': current_content['timestamp']
            })
            
        return changes
