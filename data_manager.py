import json
from typing import List, Dict, Any
from datetime import datetime
import os

class DataManager:
    def __init__(self):
        self.changes_file = "changes.json"
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Create changes file if it doesn't exist"""
        if not os.path.exists(self.changes_file):
            with open(self.changes_file, 'w') as f:
                json.dump([], f)
                
    def store_changes(self, changes: List[Dict[str, Any]]):
        """Store detected changes"""
        try:
            # Read existing changes
            with open(self.changes_file, 'r') as f:
                existing_changes = json.load(f)
                
            # Add new changes
            for change in changes:
                change['timestamp'] = datetime.now().isoformat()
                existing_changes.append(change)
                
            # Keep only last 100 changes
            if len(existing_changes) > 100:
                existing_changes = existing_changes[-100:]
                
            # Save changes
            with open(self.changes_file, 'w') as f:
                json.dump(existing_changes, f, indent=2)
                
        except Exception as e:
            raise Exception(f"Failed to store changes: {str(e)}")
            
    def get_recent_changes(self) -> List[Dict[str, Any]]:
        """Retrieve recent changes"""
        try:
            with open(self.changes_file, 'r') as f:
                changes = json.load(f)
            return changes[-10:]  # Return last 10 changes
            
        except Exception as e:
            raise Exception(f"Failed to retrieve changes: {str(e)}")
