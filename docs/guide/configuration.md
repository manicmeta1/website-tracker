# Configuration Guide

## Website Monitoring Settings

Configure which websites to monitor and how often to check for changes. Create a `website_config.json` file:

```json
{
  "urls": [
    {
      "url": "https://example.com",
      "check_interval": "1h",
      "notify_on_change": true,
      "monitor_sections": ["content", "links", "images"],
      "ignore_patterns": [
        "timestamp",
        "advertisement"
      ]
    }
  ]
}
```

## Notification Settings

Configure notification preferences in `user_preferences.json`:

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "address": "your-email@example.com"
    },
    "minimum_significance": 5,
    "notify_on": ["critical", "high"]
  }
}
```

## OpenAI Integration

Set up the OpenAI API integration for change analysis:

1. Set your API key in the environment:
```bash
export OPENAI_API_KEY=your_api_key_here
```

2. Configure analysis preferences:
```json
{
  "ai_settings": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "analysis_depth": "detailed",
    "significance_threshold": 3
  }
}
```

## Advanced Settings

### Change Detection

Fine-tune change detection sensitivity:

```json
{
  "detection": {
    "text_similarity_threshold": 0.8,
    "visual_diff_threshold": 0.1,
    "min_changes_to_report": 1
  }
}
```

### Timeline Visualization

Configure timeline display options:

```json
{
  "timeline": {
    "max_entries": 100,
    "group_by": "url",
    "sort_order": "newest_first",
    "highlight_changes": true
  }
}
```

For more detailed monitoring options, see the [Monitoring Features](monitoring.md) guide.