import pandas as pd
import numpy as np
from datetime import datetime
import re

class TransformData:   
    def __init__(self):
        self.exchange_rate = 16000  # ubah dari USD ke Rupiah
    
    def process(self, products: list) -> pd.DataFrame:
        df = pd.DataFrame(products)
        
        if df.empty:
            return df
        
        df = df[~df['Title'].str.contains('unknown', case=False, na=False)]
        df['Price'] = (
            df['Price'].str.replace(r'[^\d.]', '', regex=True).replace('', np.nan).astype(float).mul(self.exchange_rate)
        )
        df['Rating'] = (
            df['Rating'].str.extract(r'(\d+\.?\d*)')[0].astype(float)
        )
        df['Color'] = (
            df['Color'].str.extract(r'(\d+)')[0].astype(int)
        )
        df['Size'] = df['Size'].str.replace(r'(?i)size:\s*', '', regex=True)
        df['Gender'] = df['Gender'].str.replace(r'(?i)gender:\s*', '', regex=True)
        return (
            df.dropna().drop_duplicates().assign(Timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )