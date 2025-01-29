# API Documentation

## Overview

The Website Tracker API provides programmatic access to website monitoring and change detection features. This documentation covers the core components and their usage.

## Core Components

### Change Detection

The change detection system provides APIs for:
- Detecting content changes
- Analyzing modifications
- Scoring change significance
- Visual difference highlighting

### Timeline Visualization

The timeline visualization component offers:
- Change history tracking
- Visual representation of changes
- Filtering and sorting capabilities
- Export functionality

## Authentication

API access requires authentication using environment variables:
- `OPENAI_API_KEY`: Required for AI-powered change analysis
- Additional keys may be required based on configuration

## Rate Limits

- Standard rate limits apply to API endpoints
- Batch operations are recommended for multiple requests
- Consider caching frequently accessed data

## Error Handling

All API endpoints follow standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Getting Started

See the individual API component documentation for detailed usage instructions:
- [Change Detection API](change-detection.md)
- [Timeline Visualization API](timeline.md)
