import requests
from bs4 import BeautifulSoup
import time
import random

class ScrapeMain:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml'
        }
    
    def fetch(self, url: str) -> list:
        page_content = self.get_html(url)
        return self.content(page_content) if page_content else []
    
    def get_html(self, url: str) -> str:
        for attempt in range(3):
            try:
                response = requests.get(
                    url, 
                    headers=self.headers,
                    timeout=15
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == 2:
                    raise ConnectionError(f"Failed to fetch {url}: {str(e)}")
                time.sleep(2 ** attempt + random.uniform(0, 1))
    
    def content(self, html: str) -> list:
        document = BeautifulSoup(html, 'html.parser') 
        product_cards = document.find_all('div', class_='collection-card')
        return [self._extract_product(card) for card in product_cards]
    
    def _extract_product(self, card) -> dict:
        return {
            'Title': self.get_text(card, 'h3', {'class': 'product-title'}),
            'Price': self.get_text(card, 'div', {'class': 'price-container'}),
            'Rating': self.find_by_label(card, 'Rating'),
            'Color': self.find_by_label(card, 'Colors'),
            'Size': self.find_by_label(card, 'Size'),
            'Gender': self.find_by_label(card, 'Gender')
        }
    
    def get_text(self, parent, tag: str, attrs: dict) -> str:
        element = parent.find(tag, attrs)
        return element.get_text(strip=True) if element else 'tidak tersedia'
    
    def find_by_label(self, parent, label: str) -> str:
        element = parent.find('p', string=lambda s: s and label.lower() in s.lower())
        return element.get_text(strip=True) if element else f'{label} label tidak ditemukan'