# Configuration Guide

## Website Monitoring Settings

Configure which websites to monitor and how often to check for changes:

```json
{
  "urls": [
    {
      "url": "https://example.com",
      "check_interval": "1h",
      "notify_on_change": true
    }
  ]
}
```

## Notification Settings

Set up email or other notification methods when changes are detected.

## OpenAI Integration

Configure the AI analysis settings to control how changes are analyzed and summarized.
