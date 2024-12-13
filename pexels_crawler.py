import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from io import BytesIO

# 加载环境变量
load_dotenv()

class PexelsCrawler:
    def __init__(self):
        self.api_key = os.getenv('PEXELS_API_KEY')
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {
            'Authorization': self.api_key
        }
        self.download_path = Path(os.getenv('DOWNLOAD_PATH', './downloads'))
        self.download_path.mkdir(parents=True, exist_ok=True)

    def search_photos(self, query, per_page=80, page=1):
        """搜索图片"""
        url = f"{self.base_url}/search"
        params = {
            'query': query,
            'per_page': per_page,
            'page': page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error searching photos: {response.status_code}")
            return None

    def download_image(self, photo):
        """下载单张图片"""
        try:
            # 获取图片URL和信息
            image_url = photo['src']['large']
            photographer = photo['photographer']
            photo_id = photo['id']
            
            # 构建文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{photo_id}_{photographer}_{timestamp}.jpg"
            filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
            
            # 下载图片
            response = requests.get(image_url)
            if response.status_code == 200:
                # 验证图片
                img = Image.open(BytesIO(response.content))
                
                # 保存图片
                file_path = self.download_path / filename
                img.save(file_path, 'JPEG')
                return True
            return False
        except Exception as e:
            print(f"Error downloading image {photo['id']}: {str(e)}")
            return False

    def crawl_indoor_photos(self, pages=1):
        """爬取室内图片"""
        total_downloaded = 0
        
        for page in range(1, pages + 1):
            print(f"\nFetching page {page}...")
            results = self.search_photos("indoor", page=page)
            
            if results and 'photos' in results:
                photos = results['photos']
                with tqdm(total=len(photos), desc="Downloading images") as pbar:
                    for photo in photos:
                        if self.download_image(photo):
                            total_downloaded += 1
                        pbar.update(1)
            
            print(f"\nPage {page} completed. Total downloaded: {total_downloaded}")

if __name__ == "__main__":
    crawler = PexelsCrawler()
    print("Starting Pexels Indoor Photos Crawler...")
    print(f"Images will be saved to: {crawler.download_path}")
    crawler.crawl_indoor_photos(pages=3)  # 下载3页图片
    print("\nCrawling completed!")
