"""
Pexels downloader configuration
"""

# API Configuration
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Secret-Key': 'H2jk9uKnhRmL6WPwh89zBezWvr'
}

# Download Configuration
DOWNLOAD_DIR = 'download'
PER_PAGE = 24
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

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
    'seo_tags': 'true'
}
