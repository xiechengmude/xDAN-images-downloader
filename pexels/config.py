"""
Pexels下载器配置文件
包含所有下载器需要的配置参数，包括路径、API设置、下载设置等
"""
import os
import yaml
import logging

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pexels模块的根目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, 'download')      # 下载文件保存的根目录

# API请求头配置
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',  # 请求语言设置
    'Authorization': 'dESvTyqCMdAFgmvWMP1N9d4rOoCWyfE3d52PFleYdrZlz0MUBjrFHbFg'  # API密钥
}

# 下载配置参数
PER_PAGE = 300                  # 每页返回的图片/视频数量
MAX_RETRIES = 3               # 下载失败时的最大重试次数
RETRY_DELAY = 2               # 重试之间的等待时间（秒）
MAX_PAGES_PER_CATEGORY = 10000  # 每个分类最多下载的页数，防止过度请求

# API端点配置
ENDPOINTS = {
    'photos': 'https://www.pexels.com/en-us/api/v3/search/photos',  # 图片搜索API端点
    'videos': 'https://www.pexels.com/en-us/api/v3/search/videos'   # 视频搜索API端点
}

# 搜索参数默认值
DEFAULT_SEARCH_PARAMS = {
    'page': '1',              # 页码，从1开始
    'per_page': str(PER_PAGE),# 每页数量
    'orientation': 'all',     # 图片方向：all-所有方向
    'size': 'all',           # 图片尺寸：all-所有尺寸
    'color': 'all',          # 颜色筛选：all-所有颜色
    'sort': 'popular',       # 排序方式：popular-按热度排序
    'seo_tags': 'true'       # 是否返回SEO标签
}

# 分类配置
# 可以在这里直接定义分类和关键词，也可以从categories.yaml文件加载
CATEGORIES = {
    'interior': [
        'interior'  # 测试关键词
    ]
}

# 日志配置
logger = logging.getLogger(__name__)

# 从YAML文件加载分类配置
def load_categories():
    """
    从categories.yaml文件加载分类配置
    Returns:
        dict: 包含分类和关键词的字典
    """
    # 先尝试加载项目根目录下的配置
    categories_file = os.path.join(PROJECT_DIR, 'categories.yaml')
    if not os.path.exists(categories_file):
        # 如果不存在，则尝试加载pexels模块目录下的配置
        categories_file = os.path.join(BASE_DIR, 'categories.yaml')
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
            logger.info(f"已加载分类配置: {categories_file}")
            return categories
    except Exception as e:
        logger.error(f"加载分类配置失败: {str(e)}")
        return {}
