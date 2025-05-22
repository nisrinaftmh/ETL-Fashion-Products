import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, Mock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.transform import TransformData


class TestTransformData(unittest.TestCase):
    def setUp(self):
        self.transformer = TransformData()
        self.sample_products = [
            {
                'Title': 'Product 1',
                'Price': '$20.50',
                'Rating': 'Rating: 4.5',
                'Color': 'Colors: 3',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            },
            {
                'Title': 'Product 2',
                'Price': '$30.75',
                'Rating': 'Rating: 3.8',
                'Color': 'Colors: 5',
                'Size': 'Size: L',
                'Gender': 'Gender: Women'
            },
            {
                'Title': 'unknown Product',
                'Price': '$15.25',
                'Rating': 'Rating: 2.5',
                'Color': 'Colors: 2',
                'Size': 'Size: S',
                'Gender': 'Gender: Unisex'
            }
        ]
    
    def test_process_with_valid_data(self):
        result = self.transformer.process(self.sample_products)

        self.assertIsInstance(result, pd.DataFrame)
        
        self.assertEqual(len(result), 2)
        

        titles = result['Title'].tolist()
        self.assertIn('Product 1', titles)
        self.assertIn('Product 2', titles)
        self.assertNotIn('unknown Product', titles)
        
        # perubahan mata uang (harga dolar * 16000 = 328000)
        product1_row = result[result['Title'] == 'Product 1']
        self.assertAlmostEqual(product1_row['Price'].iloc[0], 20.50 * 16000)
    
        product2_row = result[result['Title'] == 'Product 2']
        self.assertAlmostEqual(product2_row['Price'].iloc[0], 30.75 * 16000)
        
        # cek rating
        self.assertAlmostEqual(product1_row['Rating'].iloc[0], 4.5)
        self.assertAlmostEqual(product2_row['Rating'].iloc[0], 3.8)
        
        # cek color
        self.assertEqual(product1_row['Color'].iloc[0], 3)
        self.assertEqual(product2_row['Color'].iloc[0], 5)
        
        # cek size
        self.assertEqual(product1_row['Size'].iloc[0], 'M')
        self.assertEqual(product2_row['Size'].iloc[0], 'L')
        
        # cek gender
        self.assertEqual(product1_row['Gender'].iloc[0], 'Men')
        self.assertEqual(product2_row['Gender'].iloc[0], 'Women')
        
        # nambahin timestamp
        self.assertTrue('Timestamp' in result.columns)
        self.assertIsNotNone(result['Timestamp'].iloc[0])
    
    def test_process_with_empty_data(self):
        result = self.transformer.process([])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_process_with_duplicate_data(self):
        duplicate_products = [
            {
                'Title': 'Product 1',
                'Price': '20000.0',
                'Rating': 'Rating: 4.5',
                'Color': 'Colors: 3',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            },
            {
                'Title': 'Product 1',  
                'Price': '20000.0',
                'Rating': 'Rating: 4.5',
                'Color': 'Colors: 3',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            }
        ]
        
        result = self.transformer.process(duplicate_products)
        self.assertEqual(len(result), 1)
    
    
    @patch('utils.transform.datetime')
    def test_timestamp_format(self, mock_datetime):
        mock_now = Mock()
        mock_now.strftime.return_value = '2023-01-01 12:00:00'
        mock_datetime.now.return_value = mock_now
        result = self.transformer.process([self.sample_products[0]])
        self.assertEqual(result['Timestamp'].iloc[0], '2023-01-01 12:00:00')


if __name__ == '__main__':
    unittest.main()