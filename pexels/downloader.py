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
from typing import List, Tuple, Dict, Optional
from . import config

warnings.filterwarnings('ignore')

class PexelsDownloader:
    def __init__(self):
        self.headers = config.HEADERS
        self.download_dir = config.DOWNLOAD_DIR

    def _request(self, url: str, params: Optional[Dict] = None, 
                data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with retry mechanism"""
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
        """Search for photos or videos"""
        url = config.ENDPOINTS[content_type]
        params = {
            **config.DEFAULT_SEARCH_PARAMS,
            'page': str(page),
            'per_page': str(config.PER_PAGE),
            'query': keyword
        }
        
        response = self._request(url, params=params)
        response_json = response.json()
        return response_json['data'], response_json['pagination']['total_pages']

    def download_file(self, content_type: str, save_path: str, url: str) -> str:
        """Download photo or video file"""
        response = requests.get(url, headers=self.headers, stream=True)
        
        if content_type == 'photos':
            file_name = save_path.split('/')[-1]
            self._save_file(save_path, response)
        else:  # videos
            file_name = self._get_video_filename(response)
            save_path = os.path.join(os.path.dirname(save_path), file_name)
            self._save_file_with_progress(save_path, response)
            
        return file_name

    def _save_file(self, path: str, response: requests.Response) -> None:
        """Save file without progress bar"""
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    def _save_file_with_progress(self, path: str, response: requests.Response) -> None:
        """Save file with progress bar"""
        file_size = int(response.headers.get('Content-length', 0))
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                progress_bar.update(len(chunk))
        progress_bar.close()

    def _get_video_filename(self, response: requests.Response) -> str:
        """Extract and clean video filename"""
        file_name = re.search('filename=(.*)', response.url).group(1)
        file_name = re.sub('\\|/|:|\*|\?|"|<|>|\||/', '', file_name)
        return unquote(file_name)

    def download_by_keywords(self, keywords: List[str], content_type: str = 'photos') -> None:
        """Main download function"""
        for keyword in keywords:
            page = 1
            while True:
                logger.debug(f'Downloading "{keyword}" page {page}')
                try:
                    data, total_pages = self.search(content_type, keyword, page)
                    
                    if not data and total_pages == 1:
                        logger.warning(f'No results found for "{keyword}"')
                        break
                        
                    if page > total_pages:
                        break

                    save_dir = os.path.join(self.download_dir, content_type, keyword)
                    os.makedirs(save_dir, exist_ok=True)

                    for index, item in enumerate(data, 1):
                        download_link = (item['attributes']['image']['download_link'] 
                                      if content_type == 'photos' 
                                      else item['attributes']['video']['download_link'])
                        
                        if content_type == 'photos':
                            file_name = unquote(re.search('dl=(.*)&', download_link).group(1))
                        else:
                            file_name = ''  # Will be determined during download
                            
                        save_path = os.path.join(save_dir, file_name)
                        
                        if os.path.exists(save_path):
                            continue
                            
                        try:
                            file_name = self.download_file(content_type, save_path, download_link)
                            logger.success(f'Download success ({index}/{len(data)}): {file_name}')
                        except Exception as e:
                            logger.error(f'Download failed ({index}/{len(data)}): {str(e)}')
                            
                    page += 1
                except Exception as e:
                    logger.error(f'Error processing page {page}: {str(e)}')
                    break
                    
        logger.success('Download completed!')
