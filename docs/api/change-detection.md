# Change Detection API

## Overview

The Change Detection API provides programmatic access to monitor and detect changes in websites. This document covers the core components and their usage.

## Components

### ChangeDetector

The `ChangeDetector` class is responsible for identifying changes in website content:

```python
from change_detector import ChangeDetector

detector = ChangeDetector()
changes = detector.detect_changes(content)
```

#### Methods

- `detect_changes(content: Dict[str, Any]) -> List[Dict[str, Any]]`
  - Detects changes between current and previous content
  - Returns a list of detected changes with metadata

### ChangeScorer

The `ChangeScorer` class analyzes and scores detected changes:

```python
from change_scorer import ChangeScorer

scorer = ChangeScorer()
scored_changes = scorer.score_changes(changes)
```

#### Methods

- `analyze_change(change: Dict[str, Any]) -> Dict[str, Any]`
  - Analyzes a single change and returns significance score
- `score_changes(changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
  - Scores multiple changes and sorts by significance

## Change Types

The API detects various types of changes:

- Text changes
- Link additions/removals
- Visual changes
- Menu structure changes
- Style modifications

## Example Usage

```python
from change_detector import ChangeDetector
from change_scorer import ChangeScorer

# Initialize components
detector = ChangeDetector()
scorer = ChangeScorer()

# Detect changes
current_content = {
    'text': 'Updated content',
    'timestamp': '2024-01-29T12:00:00Z',
    'pages': [{'url': 'example.com', 'location': '/'}]
}

changes = detector.detect_changes(current_content)
scored_changes = scorer.score_changes(changes)

# Process scored changes
for change in scored_changes:
    print(f"Change type: {change['type']}")
    print(f"Significance: {change['significance_score']}")
    print(f"Analysis: {change['analysis']}")
```

## Error Handling

The API uses standard Python exceptions:

- `ValueError`: Invalid input parameters
- `KeyError`: Missing required fields
- `Exception`: General errors during processing

## Best Practices

1. **Regular Monitoring**
   - Maintain consistent check intervals
   - Handle rate limits appropriately

2. **Error Handling**
   - Implement proper exception handling
   - Log errors for debugging

3. **Performance**
   - Cache frequently accessed data
   - Use batch processing for multiple changes

4. **Security**
   - Validate input data
   - Handle sensitive information securely
