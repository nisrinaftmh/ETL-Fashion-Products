from utils.extract import ScrapeMain
from utils.transform import TransformData
from utils.load import SaveToCSV
import time

def main():
    base_url = 'https://fashion-studio.dicoding.dev/'
    extractor = ScrapeMain()
    transformer = TransformData()
    saver = SaveToCSV()
    
    all_products = []
    total_pages = 50
    
    
    for page in range(1, total_pages + 1):
        url = f"{base_url}page{page}" if page > 1 else base_url
        try:
            print(f"Melakukan Scrapping pada halaman {page}/{total_pages}...", end=' ', flush=True)
            products = extractor.fetch(url)
            all_products.extend(products)
            print(f"Ditemukan {len(products)} produk")
        except Exception as e:
            print(f"Error ditemukan pada halaman {page}: {str(e)}")
            continue
    print(f"Total produk terkumpul sebanyak {len(all_products)} produk")
    
    if all_products:
        print("Proses data dimulai")
        clean_data = transformer.process(all_products)
        print(f"Setelah Proses data ditemukan {len(clean_data)} data produk yang valid")
        saver.save(clean_data)
    else:
        print("Tidak berhasil Scrapping")

if __name__ == '__main__':
    main()