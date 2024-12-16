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

    def download_all_categories(self, content_type: str, use_category_only: bool = False):
        """下载所有分类的内容
        Args:
            content_type: 内容类型（photos/videos）
            use_category_only: 是否只使用分类名称搜索，忽略关键词
        """
        logger.info(f"Starting download for all categories, type: {content_type}")
        
        for category, keywords in config.CATEGORIES.items():
            try:
                self.process_category(category, keywords, content_type, use_category_only)
            except Exception as e:
                logger.error(f"Error processing category {category}: {str(e)}")
                continue
        
        self._download_stats.log_summary()
    
    def process_category(self, category: str, keywords: List[str], content_type: str, use_category_only: bool = False):
        """处理单个分类
        Args:
            category: 分类名称
            keywords: 关键词列表
            content_type: 内容类型（photos/videos）
            use_category_only: 是否只使用分类名称搜索，忽略关键词
        """
        logger.info(f"Processing category: {category}")
        
        # 如果设置了只使用分类名称，或关键词列表为空
        if use_category_only or not keywords or (len(keywords) == 1 and not keywords[0].strip()):
            self._process_single_keyword(category, category, content_type)
            return
            
        # 否则使用关键词+分类名称搜索
        for keyword in keywords:
            if not keyword.strip():  # 跳过空关键词
                continue
                
            # 如果关键词不包含分类名，自动添加分类名作为后缀
            search_keyword = keyword
            if category not in keyword.lower():
                search_keyword = f"{keyword} {category}"
            
            self._process_single_keyword(category, search_keyword, content_type)
    
    def _process_single_keyword(self, category: str, keyword: str, content_type: str):
        """处理单个关键词的搜索和下载"""
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
                logger.debug(f"API Response: Status={response.status_code}, URL={response.url}")
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('data'):
                        logger.warning(f"API返回成功但没有数据: {data}")
                    return data.get('data', []), data.get('pagination', {}).get('total_pages', 1)
                elif response.status_code == 401:
                    logger.error("API认证失败，请检查 API key 是否正确")
                    raise Exception("API认证失败")
                else:
                    logger.error(f"API请求失败: status_code={response.status_code}, response={response.text}")
                    raise Exception(f"API请求失败: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"搜索内容时出错: {str(e)}")
                time.sleep(config.RETRY_DELAY)
                raise

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
