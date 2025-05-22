import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.extract import ScrapeMain


class TestScrapeMain(unittest.TestCase):
    def setUp(self):
        self.scraper = ScrapeMain()
        self.test_url = "https://fashion-studio.dicoding.dev/"
        
    @patch('utils.extract.requests.get')
    def test_get_html_success(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.scraper.get_html(self.test_url)
        
        self.assertEqual(result, "<html><body>Test content</body></html>")
        mock_get.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
        
    @patch('utils.extract.requests.get')
    def test_get_html_retry_success(self, mock_get):
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.RequestException("Connection error")
        
        mock_response_success = Mock()
        mock_response_success.text = "<html><body>Test content</body></html>"

        mock_response_success.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        with patch('utils.extract.time.sleep', return_value=None):  
            result = self.scraper.get_html(self.test_url)

        self.assertEqual(result, "<html><body>Test content</body></html>")
        self.assertEqual(mock_get.call_count, 2)
        
    @patch('utils.extract.requests.get')
    def test_get_html_all_retries_fail(self, mock_get):
        mock_get.side_effect = [
            requests.RequestException("Connection error"),
            requests.RequestException("Connection error"),
            requests.RequestException("Connection error")
        ]
        
        with patch('utils.extract.time.sleep', return_value=None): 
            with self.assertRaises(ConnectionError):
                self.scraper.get_html(self.test_url)
        
        self.assertEqual(mock_get.call_count, 3)
        
    @patch('utils.extract.ScrapeMain.get_html')
    @patch('utils.extract.ScrapeMain.content')
    def test_fetch_success(self, mock_content, mock_get_html):

        mock_get_html.return_value = "<html><body>Test content</body></html>"
        mock_content.return_value = [{'Title': 'Product 1', 'Price': '$20.00'}]
        
        result = self.scraper.fetch(self.test_url)

        self.assertEqual(result, [{'Title': 'Product 1', 'Price': '$20.00'}])
        mock_get_html.assert_called_once_with(self.test_url)
        mock_content.assert_called_once_with("<html><body>Test content</body></html>")
        
    @patch('utils.extract.ScrapeMain.get_html')
    def test_fetch_failed_connection(self, mock_get_html):
        mock_get_html.return_value = None

        result = self.scraper.fetch(self.test_url)

        self.assertEqual(result, [])
        
    @patch('utils.extract.BeautifulSoup')
    def test_content_parsing(self, mock_bs):
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        
        mock_card1 = MagicMock()
        mock_card2 = MagicMock()
        mock_soup.find_all.return_value = [mock_card1, mock_card2]
        
        with patch.object(self.scraper, '_extract_product') as mock_extract:
            mock_extract.side_effect = [
                {'Title': 'Product 1', 'Price': '$20.00'},
                {'Title': 'Product 2', 'Price': '$30.00'}
            ]
            
            result = self.scraper.content("<html><body>Test content</body></html>")
            
            self.assertEqual(result, [
                {'Title': 'Product 1', 'Price': '$20.00'},
                {'Title': 'Product 2', 'Price': '$30.00'}
            ])
            mock_bs.assert_called_once_with("<html><body>Test content</body></html>", 'html.parser')
            mock_soup.find_all.assert_called_once_with('div', class_='collection-card')
            self.assertEqual(mock_extract.call_count, 2)
            
    def test_extract_product(self):
        card = MagicMock()
        
        with patch.object(self.scraper, 'get_text') as mock_get_text:
            with patch.object(self.scraper, 'find_by_label') as mock_find_by_label:
                mock_get_text.side_effect = [
                    'Test Product',  
                    '$25.99'         
                ]
                mock_find_by_label.side_effect = [
                    '4.5 stars',     
                    'Red, Blue',     
                    'M, L, XL',      
                    'Unisex'         
                ]
                
                result = self.scraper._extract_product(card)
                
                expected = {
                    'Title': 'Test Product',
                    'Price': '$25.99',
                    'Rating': '4.5 stars',
                    'Color': 'Red, Blue',
                    'Size': 'M, L, XL',
                    'Gender': 'Unisex'
                }
                self.assertEqual(result, expected)
                
                mock_get_text.assert_any_call(card, 'h3', {'class': 'product-title'})
                mock_get_text.assert_any_call(card, 'div', {'class': 'price-container'})
                mock_find_by_label.assert_any_call(card, 'Rating')
                mock_find_by_label.assert_any_call(card, 'Colors')
                mock_find_by_label.assert_any_call(card, 'Size')
                mock_find_by_label.assert_any_call(card, 'Gender')
    
    def test_get_text_element_exists(self):
        parent = MagicMock()
        element = MagicMock()
        element.get_text.return_value = "Test Value"
        parent.find.return_value = element

        result = self.scraper.get_text(parent, 'span', {'class': 'test-class'})
        
        self.assertEqual(result, "Test Value")
        parent.find.assert_called_once_with('span', {'class': 'test-class'})
        element.get_text.assert_called_once_with(strip=True)
        
    def test_get_text_element_not_exists(self):
        parent = MagicMock()
        parent.find.return_value = None

        result = self.scraper.get_text(parent, 'span', {'class': 'test-class'})

        self.assertEqual(result, "tidak tersedia")
        parent.find.assert_called_once_with('span', {'class': 'test-class'})
        
    def test_find_by_label_element_exists(self):
        parent = MagicMock()
        element = MagicMock()

        element.get_text.return_value = "Rating: 4.5 stars"
        parent.find.return_value = element
        
        result = self.scraper.find_by_label(parent, 'Rating')

        self.assertEqual(result, "Rating: 4.5 stars")
        parent.find.assert_called_once()
        element.get_text.assert_called_once_with(strip=True)
        
    def test_find_by_label_element_not_exists(self):
        parent = MagicMock()
        parent.find.return_value = None
        
        result = self.scraper.find_by_label(parent, 'Rating')

        self.assertEqual(result, "Rating label tidak ditemukan")
        parent.find.assert_called_once()


if __name__ == '__main__':
    unittest.main()