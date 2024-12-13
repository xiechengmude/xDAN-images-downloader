"""
Pexels image and video downloader
"""
from requests.compat import unquote
from loguru import logger
from tqdm import tqdm
import time
import os
import re
import requests
import warnings
import concurrent.futures
import multiprocessing
from typing import List, Tuple, Dict, Optional
import psutil
from . import config

warnings.filterwarnings('ignore')

class PexelsDownloader:
    def __init__(self):
        self.headers = config.HEADERS
        self.download_dir = config.DOWNLOAD_DIR
        
    def get_optimal_workers(self):
        """根据CPU使用情况动态确定最优的工作进程数"""
        cpu_count = multiprocessing.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent < 50:
            return max(cpu_count - 1, 1)
        elif cpu_percent < 75:
            return max(cpu_count // 2, 1)
        else:
            return max(cpu_count // 4, 1)

    def _request(self, url: str, params: Optional[Dict] = None, 
                data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """发送请求并处理重试"""
        method = 'post' if (data or json) else 'get'
        for _ in range(config.MAX_RETRIES):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    json=json
                )
                if response.status_code in [200, 302, 401]:
                    return response
                raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                logger.debug(f"Request failed: {str(e)} (retrying...)")
                time.sleep(config.RETRY_DELAY)
        raise Exception(f"Failed after {config.MAX_RETRIES} retries")

    def search(self, content_type: str, keyword: str, page: int = 1) -> Tuple[List, int]:
        """搜索图片或视频"""
        url = config.ENDPOINTS[content_type]
        params = {
            **config.DEFAULT_SEARCH_PARAMS,
            'page': str(page),
            'query': keyword
        }
        
        response = self._request(url, params=params)
        response_json = response.json()
        return response_json['data'], response_json['pagination']['total_pages']

    def download_file(self, url: str, save_path: str, content_type: str = 'photos') -> Optional[str]:
        """下载单个文件"""
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            if response.status_code == 200:
                if content_type == 'photos':
                    file_name = re.search('dl=(.*)&', url).group(1)
                    file_name = unquote(file_name)
                else:  # videos
                    file_name = re.search('filename=(.*)', response.url).group(1)
                    file_name = re.sub('\\|/|:|\*|\?|"|<|>|\||/', '', file_name)
                    file_name = unquote(file_name)

                file_path = os.path.join(save_path, file_name)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return file_name
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
        return None

    def process_category(self, category: str, subcategories: List[str], content_type: str = 'photos'):
        """处理单个主分类下的所有子分类"""
        logger.info(f"Processing category: {category}")
        
        # 创建分类目录
        category_dir = os.path.join(self.download_dir, content_type, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 获取最优的工作进程数
        workers = self.get_optimal_workers()
        logger.info(f"Using {workers} worker processes")
        
        for subcategory in subcategories:
            subcategory_dir = os.path.join(category_dir, subcategory.replace(' ', '_'))
            os.makedirs(subcategory_dir, exist_ok=True)
            
            logger.info(f"Downloading {subcategory}")
            page = 1
            
            while page <= config.MAX_PAGES_PER_CATEGORY:
                try:
                    data, total_pages = self.search(content_type, subcategory, page)
                    if not data:
                        break
                        
                    # 并发下载图片
                    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                        future_to_url = {}
                        for item in data:
                            download_link = (item['attributes']['image']['download_link'] 
                                          if content_type == 'photos' 
                                          else item['attributes']['video']['download_link'])
                            future = executor.submit(self.download_file, download_link, subcategory_dir, content_type)
                            future_to_url[future] = download_link
                            
                        # 处理下载结果
                        for future in tqdm(
                            concurrent.futures.as_completed(future_to_url),
                            total=len(future_to_url),
                            desc=f"Downloading {subcategory} page {page}"
                        ):
                            url = future_to_url[future]
                            try:
                                filename = future.result()
                                if filename:
                                    logger.debug(f"Downloaded: {filename}")
                            except Exception as e:
                                logger.error(f"Failed to download {url}: {str(e)}")
                                
                    page += 1
                    if page > total_pages:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing page {page} of {subcategory}: {str(e)}")
                    break
                    
            logger.success(f"Completed downloading {subcategory}")

    def download_all_categories(self, content_type: str = 'photos'):
        """下载所有分类的内容"""
        logger.info("Starting download of all categories")
        
        for category, subcategories in config.CATEGORIES.items():
            try:
                self.process_category(category, subcategories, content_type)
            except Exception as e:
                logger.error(f"Error processing category {category}: {str(e)}")
                continue
                
        logger.success("All categories downloaded successfully!")
