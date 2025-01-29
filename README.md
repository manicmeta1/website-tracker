# Website Monitor

A comprehensive AI-powered website monitoring platform that leverages advanced web scraping and intelligent analysis technologies to provide real-time change detection and insights across multiple websites.

## Features

- Real-time website monitoring
- AI-powered change detection and analysis
- Visual diff highlighting
- Timeline visualization of changes
- Customizable monitoring preferences
- Email notifications
- Multi-website support

## Deployment Guide

### Prerequisites

This application requires Python 3.11 and the following packages:
- streamlit
- selenium
- openai
- beautifulsoup4
- diff-match-patch
- pandas
- pillow
- requests
- trafilatura
- apscheduler

### Deployment Options

#### 1. Streamlit Cloud (Recommended)

The easiest way to deploy this application is using [Streamlit Cloud](https://streamlit.io/cloud):

1. Create a Streamlit Cloud account
2. Connect your GitHub repository
3. Select your repository and branch
4. Enter the following settings:
   - Main file path: `main.py`
   - Python version: 3.11
5. Add your secrets in the Streamlit Cloud dashboard:
   - OPENAI_API_KEY: Your OpenAI API key

#### 2. Custom Server Deployment

To deploy on your own server:

1. Clone your repository to your server
2. Install Python 3.11
3. Install system dependencies:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install chromium-browser chromium-chromedriver
   ```

4. Install Python dependencies:
   ```bash
   pip install streamlit selenium openai beautifulsoup4 diff-match-patch pandas pillow requests trafilatura apscheduler
   ```

5. Set up environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

6. Start the application:
   ```bash
   streamlit run main.py --server.port=8501 --server.address=0.0.0.0
   ```

7. For production deployment, it's recommended to use a process manager like Supervisor:

   Create a supervisor config file `/etc/supervisor/conf.d/website-monitor.conf`:
   ```ini
   [program:website-monitor]
   command=streamlit run main.py --server.port=8501 --server.address=0.0.0.0
   directory=/path/to/your/app
   user=your_user
   autostart=true
   autorestart=true
   stopasgroup=true
   killasgroup=true
   stderr_logfile=/var/log/website-monitor/err.log
   stdout_logfile=/var/log/website-monitor/out.log
   ```

8. Set up a reverse proxy (nginx recommended) to handle HTTPS and domain routing.

### Important Notes

1. Make sure to set up proper security measures:
   - Use HTTPS
   - Set up authentication
   - Secure your API keys
   - Configure firewall rules

2. Database considerations:
   - The app uses JSON files for storage by default
   - For production, consider migrating to a proper database system

3. Monitoring:
   - Set up logging
   - Configure system monitoring
   - Set up alerts for system health

4. Scaling:
   - Consider using multiple workers for the Streamlit application
   - Set up load balancing if needed
   - Monitor system resources and scale accordingly

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for AI analysis features

## Support

For issues and support:
1. Check the GitHub issues
2. Review the Streamlit documentation
3. Contact your system administrator for deployment-specific issues
