import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any
import hashlib
from urllib.parse import urlparse, urljoin

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding https:// if no scheme is provided
        """
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"https://{url}"
        return url

    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrapes website content and returns structured data
        """
        try:
            # Normalize URL
            url = self._normalize_url(url)

            # Get raw HTML
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            html_content = response.text

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract text content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            text_content = trafilatura.extract(downloaded)

            # Extract links
            links = [self._normalize_url(a.get('href')) for a in soup.find_all('a', href=True)]

            # Create content fingerprint
            content_hash = hashlib.md5(html_content.encode()).hexdigest()

            return {
                'url': url,
                'timestamp': response.headers.get('Date'),
                'html_content': html_content,
                'text_content': text_content,
                'links': links,
                'content_hash': content_hash
            }

        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")