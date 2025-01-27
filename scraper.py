import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, List
import hashlib
from urllib.parse import urlparse, urljoin
import time
import random
from screenshot_manager import ScreenshotManager

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.screenshot_manager = ScreenshotManager()
        self.visited_urls = set()  # Track visited URLs to avoid duplicates

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by adding https:// if no scheme is provided"""
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"https://{url}"
        return url

    def _extract_styles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract CSS styles and font information"""
        styles = {
            'fonts': set(),
            'text_sizes': set(),
            'colors': set()
        }

        # Extract inline styles
        for element in soup.find_all(style=True):
            style = element['style'].lower()
            if 'font-family' in style:
                styles['fonts'].add(style.split('font-family:')[1].split(';')[0].strip())
            if 'font-size' in style:
                styles['text_sizes'].add(style.split('font-size:')[1].split(';')[0].strip())
            if 'color' in style:
                styles['colors'].add(style.split('color:')[1].split(';')[0].strip())

        # Extract CSS from style tags
        for style in soup.find_all('style'):
            css_text = style.string
            if css_text:
                if 'font-family' in css_text.lower():
                    fonts = [f.split(':')[1].split(';')[0].strip()
                             for f in css_text.lower().split('font-family') if ':' in f]
                    styles['fonts'].update(fonts)

        return {k: sorted(list(v)) for k, v in styles.items()}

    def _extract_menu_structure(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract navigation menu structure"""
        menus = []
        nav_elements = soup.find_all(['nav', 'ul', 'menu'])

        for nav in nav_elements:
            menu_items = nav.find_all('a')
            if menu_items:
                menu = []
                for item in menu_items:
                    menu.append({
                        'text': item.get_text().strip(),
                        'href': item.get('href', ''),
                        'class': ' '.join(item.get('class', [])),
                    })
                menus.append(menu)

        return menus

    def _scrape_single_page(self, url: str) -> Dict[str, Any]:
        """Scrapes a single page and returns its content"""
        if url in self.visited_urls:
            print(f"Skipping already visited URL: {url}")
            return None

        print(f"Navigating to URL: {url}")
        self.visited_urls.add(url)

        try:
            # Get raw HTML
            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html_content = response.text

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Capture screenshot
            print("Capturing screenshot...")
            screenshot_path = self.screenshot_manager.capture_screenshot(url)
            print(f"Saving screenshot to: {screenshot_path}")

            # Extract text content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise Exception("Failed to download content")

            text_content = trafilatura.extract(downloaded)
            if not text_content:
                text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])

            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href:
                    full_url = urljoin(url, href)
                    links.append(self._normalize_url(full_url))

            print(f"Found {len(links)} links on page {url}")

            # Create content fingerprint
            content_hash = hashlib.md5(html_content.encode()).hexdigest()

            # Return page data including URL
            return {
                'url': url,  # Add URL to the page data
                'timestamp': response.headers.get('Date', time.strftime('%Y-%m-%d %H:%M:%S')),
                'html_content': html_content,
                'text_content': text_content,
                'links': links,
                'content_hash': content_hash,
                'screenshot_path': screenshot_path
            }

        except Exception as e:
            print(f"Error scraping page {url}: {str(e)}")
            return None

    def scrape_website(self, url: str, crawl_all_pages: bool = False) -> Dict[str, Any]:
        """Scrapes website content and returns structured data"""
        try:
            # Normalize URL
            url = self._normalize_url(url)
            base_domain = urlparse(url).netloc

            # Initialize results
            pages_data = []  # Store pages data here
            self.visited_urls.clear()  # Reset visited URLs for new scrape

            # Scrape initial URL
            print(f"Starting scrape of {url}")  # Debug log
            initial_page = self._scrape_single_page(url)
            if not initial_page:
                raise Exception(f"Failed to scrape initial page: {url}")

            pages_data.append({
                'url': url,
                'location': '/',  # Root page
                'content': initial_page
            })

            # If crawling is enabled, follow links within the same domain
            if crawl_all_pages:
                urls_to_visit = set([
                    link for link in initial_page['links']
                    if urlparse(link).netloc == base_domain
                ])

                print(f"Found {len(urls_to_visit)} additional pages to crawl")  # Debug log

                while urls_to_visit and len(pages_data) < 50:  # Limit to 50 pages
                    next_url = urls_to_visit.pop()
                    print(f"Crawling: {next_url}")  # Debug log

                    if next_url not in self.visited_urls:
                        try:
                            # Add small delay between requests
                            time.sleep(random.uniform(1, 2))

                            page_data = self._scrape_single_page(next_url)
                            if page_data:
                                # Extract page location from URL
                                parsed_url = urlparse(next_url)
                                location = parsed_url.path if parsed_url.path else '/'

                                pages_data.append({
                                    'url': next_url,
                                    'location': location,
                                    'content': page_data
                                })

                                # Add new links to visit
                                new_links = set([
                                    link for link in page_data['links']
                                    if urlparse(link).netloc == base_domain
                                ])
                                urls_to_visit.update(new_links - self.visited_urls)

                        except Exception as e:
                            print(f"Error crawling {next_url}: {str(e)}")
                            continue

            print(f"Completed scrape. Found {len(pages_data)} pages")  # Debug log

            # Create the combined content structure
            combined_content = {
                'url': url,
                'timestamp': initial_page['timestamp'],
                'text_content': initial_page['text_content'],
                'links': initial_page['links'],
                'content_hash': initial_page['content_hash'],
                'screenshot_path': initial_page['screenshot_path'],
                'pages': pages_data,  # Include all pages data
                'crawl_all_pages': crawl_all_pages
            }

            return combined_content

        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")