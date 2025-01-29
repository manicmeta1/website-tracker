# Getting Started

## Prerequisites

- Python 3.11 or higher
- OpenAI API key for change analysis
- Chrome/Firefox for web scraping
- Git for version control

## Installation

1. Clone the repository:
```bash
git clone https://github.com/manicmeta1/website-tracker.git
cd website-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

4. Start the application:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:5000`

## First Steps

1. Add websites to monitor in the configuration section
2. Set up monitoring preferences
3. View the timeline of detected changes
4. Configure notification settings

## Development Setup

For development:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Build documentation locally:
```bash
mkdocs serve
```

Visit the [Configuration Guide](configuration.md) for detailed settings.