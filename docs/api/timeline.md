# Timeline Visualization API

## Overview

The Timeline Visualization API provides tools to display and analyze website changes over time. This document covers the visualization components and their usage.

## Components

### TimelineVisualizer

The `TimelineVisualizer` class manages the visualization of changes:

```python
from timeline_visualizer import TimelineVisualizer

visualizer = TimelineVisualizer()
visualizer.visualize_timeline(changes)
```

#### Methods

- `visualize_timeline(changes: List[Dict[str, Any]]) -> None`
  - Creates an interactive timeline visualization
  - Supports filtering and sorting options

### Visualization Features

- Change significance indicators
- Interactive tooltips
- Filtering by date range
- Website-specific views
- Comparative analysis tools

## Configuration

### Significance Levels

The API uses color-coded significance levels:

- Critical (8-10): Major impact changes
- High (6-7): Significant modifications
- Medium (4-5): Moderate changes
- Low (1-3): Minor updates

### Display Options

```python
# Example configuration
timeline_config = {
    'max_entries': 100,
    'group_by': 'url',
    'sort_order': 'newest_first',
    'highlight_changes': True
}
```

## Example Usage

```python
from timeline_visualizer import TimelineVisualizer
import streamlit as st

# Initialize visualizer
visualizer = TimelineVisualizer()

# Example changes data
changes = [
    {
        'type': 'text_change',
        'timestamp': '2024-01-29T12:00:00Z',
        'location': '/homepage',
        'significance_score': 8,
        'analysis': {
            'impact_category': 'Content',
            'business_relevance': 'High'
        }
    }
]

# Display timeline
visualizer.visualize_timeline(changes)
```

## Views and Analysis

### Comparison View

Compare changes between different timestamps:

```python
visualizer._render_comparison_view(changes_df)
```

### Analytics View

Display change statistics and trends:

```python
visualizer._render_analytics_view(changes_df)
```

## Best Practices

1. **Performance**
   - Limit the number of displayed entries
   - Use efficient data structures
   - Implement pagination for large datasets

2. **User Experience**
   - Provide clear visual indicators
   - Maintain consistent styling
   - Include helpful tooltips

3. **Customization**
   - Allow user preferences
   - Support different visualization modes
   - Enable export capabilities

## Integration

The Timeline Visualization API integrates with:

- Streamlit components
- Change Detection API
- Data storage systems
