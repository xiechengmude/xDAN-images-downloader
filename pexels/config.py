"""
Pexels下载器配置文件
包含所有下载器需要的配置参数，包括路径、API设置、下载设置等
"""
import os
import yaml

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pexels模块的根目录
CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
DOWNLOAD_DIR = os.path.join(CURRENT_DIR, 'download')      # 下载文件保存的根目录

# API请求头配置
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',  # 请求语言设置
    'Authorization': 'dESvTyqCMdAFgmvWMP1N9d4rOoCWyfE3d52PFleYdrZlz0MUBjrFHbFg'  # 在这里填入你的 Pexels API key
}

# 下载配置参数
PER_PAGE = 500                # 每页返回的图片/视频数量
MAX_RETRIES = 3               # 下载失败时的最大重试次数
RETRY_DELAY = 2               # 重试之间的等待时间（秒）
MAX_PAGES_PER_CATEGORY = 1000    # 每个分类最多下载的页数，防止过度请求

# API端点配置
ENDPOINTS = {
    'photos': 'https://api.pexels.com/v1/search',  # 图片搜索API端点
    'videos': 'https://api.pexels.com/videos/search'   # 视频搜索API端点
}

# 搜索参数默认值
DEFAULT_SEARCH_PARAMS = {
    'per_page': str(PER_PAGE),# 每页数量
    'size': 'large'  # 图片尺寸
}

# 分类配置
# 从YAML文件加载分类配置
def load_categories():
    """
    从categories.yaml文件加载分类配置
    Returns:
        dict: 包含分类和关键词的字典
    """
    categories_file = os.path.join(CURRENT_DIR, 'categories.yaml')
    if os.path.exists(categories_file):
        with open(categories_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

# 加载分类配置
CATEGORIES = load_categories()
