import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any
import hashlib
from urllib.parse import urlparse, urljoin
import time
import random

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
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

            # Add a small random delay to seem more human-like
            time.sleep(random.uniform(1, 3))

            # Get raw HTML
            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html_content = response.text

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract text content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise Exception("Failed to download content")

            text_content = trafilatura.extract(downloaded)
            if not text_content:
                # Fallback to BeautifulSoup if trafilatura fails
                text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])

            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href:
                    full_url = urljoin(url, href)
                    links.append(self._normalize_url(full_url))

            # Create content fingerprint
            content_hash = hashlib.md5(html_content.encode()).hexdigest()

            return {
                'url': url,
                'timestamp': response.headers.get('Date', time.strftime('%Y-%m-%d %H:%M:%S')),
                'html_content': html_content,
                'text_content': text_content,
                'links': links,
                'content_hash': content_hash
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(f"Access forbidden - website may be blocking automated access. Try again later or contact the website administrator.")
            elif e.response.status_code == 404:
                raise Exception(f"Page not found - please check if the URL is correct.")
            elif e.response.status_code == 429:
                raise Exception(f"Too many requests - please wait a while before trying again.")
            else:
                raise Exception(f"HTTP error occurred: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to scrape website: {str(e)}")
        except Exception as e:
            raise Exception(f"Error while scraping: {str(e)}")