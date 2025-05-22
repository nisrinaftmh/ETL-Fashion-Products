import pandas as pd
import logging

class SaveToCSV:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def save(self, data, filename="fashion_products_clean.csv"):
        try:
            if data.empty:
                self.logger.warning("data gagal disimpan")
                return False  
            
            data.to_csv(filename, index=False)
            self.logger.info(
                f"Data berhasil disimpan sebanyak {len(data)} ke {filename}"
            )
            return True  
        except Exception as e:
            self.logger.error(f"gagal menyimpan data: {str(e)}")
            return False  