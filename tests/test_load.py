import unittest
import pandas as pd
import os
import sys
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.load import SaveToCSV

class TestSaveToCSV(unittest.TestCase):
    def setUp(self):
        self.saver = SaveToCSV()
        self.test_filename = "test_output.csv"
        self.sample_data = pd.DataFrame({
            'Title': ['Product 1', 'Product 2'],
            'Price': [100000, 200000],
            'Rating': [4.5, 3.5]
        })
        
        self._cleanup_test_files()

    def tearDown(self):
        self._cleanup_test_files()

    def _cleanup_test_files(self):
        test_files = [self.test_filename, "databaru.csv"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_save_success(self):
        result = self.saver.save(self.sample_data, self.test_filename)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_filename))
        df_read = pd.read_csv(self.test_filename)
        self.assertEqual(len(df_read), 2)
        self.assertListEqual(list(df_read.columns), list(self.sample_data.columns))

    def test_save_empty_dataframe(self):
        empty_df = pd.DataFrame()
        
        with patch.object(self.saver.logger, 'warning') as mock_warning:
            result = self.saver.save(empty_df, self.test_filename)
            
            mock_warning.assert_called_once_with("data gagal disimpan")
            self.assertFalse(result)
            self.assertFalse(os.path.exists(self.test_filename))

    @patch('pandas.DataFrame.to_csv')
    def test_save_logs_success(self, mock_to_csv):
        with patch.object(self.saver.logger, 'info') as mock_info:
            result = self.saver.save(self.sample_data, self.test_filename)
            self.assertTrue(result)
            mock_info.assert_called_once_with(
                f"Data berhasil disimpan sebanyak {len(self.sample_data)} ke {self.test_filename}"
            )
            mock_to_csv.assert_called_once()

    @patch('pandas.DataFrame.to_csv')
    def test_save_handles_exceptions(self, mock_to_csv):
        mock_to_csv.side_effect = Exception("Simulated error")
        
        with patch.object(self.saver.logger, 'error') as mock_error:
            result = self.saver.save(self.sample_data, self.test_filename)
            
            self.assertFalse(result)
            mock_error.assert_called_once()

    def test_save_custom_filename(self):
        custom_filename = "databaru.csv"
        result = self.saver.save(self.sample_data, custom_filename)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(custom_filename))
        df_read = pd.read_csv(custom_filename)
        self.assertEqual(len(df_read), len(self.sample_data))

if __name__ == '__main__':
    unittest.main()