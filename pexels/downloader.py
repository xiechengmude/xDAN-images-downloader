"""
Pexels image and video downloader with optimized resource usage
"""
import os
import re
import time
from typing import List, Dict
import requests
from requests.compat import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from loguru import logger

from . import config

class DownloadStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failure = 0
    
    def increment_success(self):
        self.success += 1
        self.total += 1
    
    def increment_failure(self):
        self.failure += 1
        self.total += 1
    
    def success_rate(self):
        return (self.success / self.total * 100) if self.total > 0 else 0
    
    def log_summary(self):
        logger.info("Download Summary:")
        logger.info(f"Total Downloads: {self.total}")
        logger.info(f"Successful: {self.success}")
        logger.info(f"Failed: {self.failure}")
        logger.info(f"Success Rate: {self.success_rate():.2f}%")

class PexelsDownloader:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(config.HEADERS)
        self._download_stats = DownloadStats()

    def download_all_categories(self, content_type: str):
        """下载所有分类的内容"""
        logger.info(f"Starting download for all categories, type: {content_type}")
        
        for category, keywords in config.CATEGORIES.items():
            try:
                self.process_category(category, keywords, content_type)
            except Exception as e:
                logger.error(f"Error processing category {category}: {str(e)}")
                continue
        
        self._download_stats.log_summary()
    
    def process_category(self, category: str, keywords: List[str], content_type: str, resolution_filter: str = None):
        """处理单个分类
        Args:
            category: 分类名称
            keywords: 关键词列表
            content_type: 内容类型 ('photos' 或 'videos')
            resolution_filter: 分辨率筛选 ('4K' 或 '8K')
        """
        logger.info(f"Processing category: {category}")
        
        for keyword in keywords:
            params = config.DEFAULT_SEARCH_PARAMS.copy()
            params['query'] = keyword
            
            page = 1
            while page <= config.MAX_PAGES_PER_CATEGORY:
                try:
                    data, total_pages = self._search_content(keyword, content_type, page)
                    
                    if not data:
                        logger.warning(f'找不到与 "{keyword}" 相关结果')
                        break
                        
                    if page >= total_pages:
                        break
                    
                    # 筛选符合分辨率要求的内容
                    if resolution_filter and resolution_filter in config.RESOLUTION_FILTERS:
                        min_width = config.RESOLUTION_FILTERS[resolution_filter]['min_width']
                        min_height = config.RESOLUTION_FILTERS[resolution_filter]['min_height']
                        
                        filtered_data = []
                        for item in data:
                            if content_type == 'photos':
                                width = item['attributes']['width']
                                height = item['attributes']['height']
                            else:  # videos
                                width = item['attributes']['video']['width']
                                height = item['attributes']['video']['height']
                            
                            if width >= min_width and height >= min_height:
                                filtered_data.append(item)
                                logger.debug(f"Found {resolution_filter} content: {width}x{height}")
                        
                        data = filtered_data
                        if not data:
                            logger.warning(f"No {resolution_filter} content found on page {page}")
                    
                    self._download_batch(data, category, keyword, content_type)
                    page += 1
                    
                except Exception as e:
                    logger.error(f"Error processing page {page} for keyword {keyword}: {str(e)}")
                    break

    def _search_content(self, keyword: str, content_type: str, page: int) -> tuple:
        """搜索内容并返回数据"""
        params = config.DEFAULT_SEARCH_PARAMS.copy()
        params.update({
            'query': keyword,
            'page': str(page)
        })
        
        while True:
            try:
                response = self._session.get(config.ENDPOINTS[content_type], params=params)
                if response.status_code in [200, 302, 401]:
                    break
                else:
                    raise Exception(response.status_code)
            except Exception as e:
                logger.debug(f"{str(e)}（请忽略，正在自动重试...）")
                time.sleep(1)
        
        data = response.json()
        return data.get('data', []), data.get('pagination', {}).get('total_pages', 1)

    def _download_batch(self, items: List[Dict], category: str, keyword: str, content_type: str):
        """批量下载内容"""
        save_dir = os.path.join(
            config.DOWNLOAD_DIR,
            content_type,
            keyword.replace(' ', '_').lower()
        )
        os.makedirs(save_dir, exist_ok=True)
        
        with tqdm(
            total=len(items),
            desc=f"{category}/{keyword}",
            unit='file',
            position=0,
            leave=True,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
        ) as main_pbar:
            
            for index, item in enumerate(items, 1):
                try:
                    if content_type == 'photos':
                        download_link = item['attributes']['image']['download_link']
                        file_name = re.search('dl=(.*)&', download_link).group(1)
                    else:
                        download_link = item['attributes']['video']['download_link']
                        file_name = ''
                        
                    file_name = unquote(file_name)
                    save_path = os.path.join(save_dir, file_name)
                    
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        logger.debug(f"File already exists: {save_path}")
                        main_pbar.update(1)
                        continue
                    
                    success = self._download_file(download_link, save_path, category, keyword)
                    
                    if success:
                        logger.success(f'下载成功（{index}/{len(items)}）：{file_name}')
                    else:
                        logger.error(f'下载失败（{index}/{len(items)}）：{file_name}')
                        
                    main_pbar.update(1)
                    main_pbar.set_postfix(
                        completed=self._download_stats.success,
                        failed=self._download_stats.failure,
                        success_rate=f"{self._download_stats.success_rate():.1f}%"
                    )
                    
                except Exception as e:
                    logger.error(f"Error downloading item {index}: {str(e)}")
                    self._download_stats.increment_failure()
                    main_pbar.update(1)
    
    def _download_file(self, url: str, save_path: str, category: str, keyword: str) -> bool:
        """下载单个文件"""
        try:
            response = self._session.get(url, stream=True)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            
            # 创建进度条
            with tqdm(
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
                desc=os.path.basename(save_path),
                leave=False
            ) as pbar:
                with open(save_path, 'wb') as f:
                    downloaded_size = 0
                    start_time = time.time()
                    
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            size = len(chunk)
                            f.write(chunk)
                            downloaded_size += size
                            pbar.update(size)
                            
                            # 计算下载速度
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0:
                                speed = downloaded_size / (1024 * 1024 * elapsed_time)  # MB/s
                                pbar.set_postfix(speed=f"{speed:.2f} MB/s", refresh=True)
            
            self._download_stats.increment_success()
            return True
            
        except Exception as e:
            self._download_stats.increment_failure()
            logger.error(f"Download failed for {url}: {str(e)}")
            return False
