"""
Pexels downloader configuration
"""
import os
import yaml

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pexels目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')  # 下载目录改为pexels/download

# API Configuration
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Secret-Key': 'H2jk9uKnhRmL6WPwh89zBezWvr'
}

# Download Configuration
PER_PAGE = 24
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
MAX_PAGES_PER_CATEGORY = 10  # 每个分类最多下载页数

# API Endpoints
ENDPOINTS = {
    'photos': 'https://www.pexels.com/en-us/api/v3/search/photos',
    'videos': 'https://www.pexels.com/en-us/api/v3/search/videos'
}

# Search Parameters
DEFAULT_SEARCH_PARAMS = {
    'orientation': 'all',
    'size': 'all',
    'color': 'all',
    'sort': 'popular',
    'seo_tags': 'true',
    'per_page': str(PER_PAGE)
}

# Load categories from YAML file
def load_categories():
    categories_file = os.path.join(CURRENT_DIR, 'categories.yaml')
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading categories: {str(e)}")
        return {}

# Categories Configuration
CATEGORIES = load_categories()
